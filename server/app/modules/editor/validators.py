from collections import defaultdict
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import DomainError
from app.modules.assets.models import MediaAsset
from app.modules.editor.schemas import TimelinePlan

EFFECT_RANGES = {
    "brightness": {"value": (-1.0, 1.0)},
    "contrast": {"value": (0.0, 4.0)},
    "saturation": {"value": (0.0, 3.0)},
    "zoom": {"value": (1.0, 4.0)},
    "pan": {"value": (-1.0, 1.0)},
    "tilt": {"value": (-1.0, 1.0)},
    "blur": {"sigma": (0.0, 20.0)},
}


async def validate_plan(
    session: AsyncSession, owner_id: UUID, project_id: UUID, plan: TimelinePlan
) -> None:
    if plan.project_id != project_id:
        raise DomainError("project_mismatch", "Timeline project does not match request", 422)
    if len(plan.clips) > get_settings().max_timeline_items:
        raise DomainError("timeline_too_large", "Timeline contains too many clips", 422)
    asset_ids = {clip.asset_id for clip in plan.clips} | {track.asset_id for track in plan.audio}
    assets = (
        await session.scalars(
            select(MediaAsset).where(
                MediaAsset.id.in_(asset_ids),
                MediaAsset.project_id == project_id,
                MediaAsset.owner_id == owner_id,
                MediaAsset.deleted_at.is_(None),
                MediaAsset.processing_status == "ready",
            )
        )
    ).all()
    by_id = {asset.id: asset for asset in assets}
    if set(by_id) != asset_ids:
        raise DomainError(
            "asset_not_found", "Every timeline asset must be ready and belong to this project", 422
        )
    clips_by_id = {clip.id: clip for clip in plan.clips}
    if len(clips_by_id) != len(plan.clips):
        raise DomainError("duplicate_clip_id", "Clip identifiers must be unique", 422)
    fps = plan.output.fps_num / plan.output.fps_den
    total = (
        max(
            [clip.timeline_start_frame + clip.duration_frames for clip in plan.clips]
            + [audio.timeline_start_frame + audio.duration_frames for audio in plan.audio]
        )
        / fps
    )
    if total > get_settings().max_project_duration_seconds:
        raise DomainError("timeline_too_long", "Timeline exceeds the configured duration", 422)
    for clip in plan.clips:
        asset = by_id[clip.asset_id]
        source_fps = asset.fps_num / asset.fps_den if asset.fps_num else fps
        source_end_seconds = (
            clip.source_in_frame / source_fps
            + clip.duration_frames * plan.output.fps_den / plan.output.fps_num
        )
        if source_end_seconds > asset.duration + 1 / source_fps:
            raise DomainError(
                "source_range_invalid", f"Clip {clip.id} extends beyond its source media", 422
            )
        for effect in clip.effects:
            allowed = EFFECT_RANGES[effect.id]
            if set(effect.parameters) != set(allowed):
                raise DomainError(
                    "effect_parameters_invalid",
                    f"Effect {effect.id} requires parameters {sorted(allowed)}",
                    422,
                )
            for name, (low, high) in allowed.items():
                value = effect.parameters[name]
                if not isinstance(value, (int, float)) or not low <= float(value) <= high:
                    raise DomainError(
                        "effect_parameters_invalid",
                        f"{effect.id}.{name} must be between {low} and {high}",
                        422,
                    )
    for track in plan.audio:
        asset = by_id[track.asset_id]
        if not asset.has_audio:
            raise DomainError(
                "audio_track_invalid", "Audio tracks must reference media with an audio stream", 422
            )
        source_fps = asset.fps_num / asset.fps_den if asset.fps_num else fps
        if (
            track.source_in_frame / source_fps + track.duration_frames / fps
            > asset.duration + 1 / source_fps
        ):
            raise DomainError(
                "audio_range_invalid", "Audio range extends beyond its source media", 422
            )
        if (
            track.fade_in_frames > track.duration_frames
            or track.fade_out_frames > track.duration_frames
        ):
            raise DomainError(
                "audio_fade_invalid", "Audio fades cannot exceed the track duration", 422
            )
    transition_pairs = set()
    for transition in plan.transitions:
        left, right = clips_by_id.get(transition.from_clip), clips_by_id.get(transition.to_clip)
        if left is None or right is None or left.track != right.track or left.id == right.id:
            raise DomainError(
                "transition_invalid", "Transition clips must exist on the same track", 422
            )
        if transition.duration_frames >= min(left.duration_frames, right.duration_frames):
            raise DomainError(
                "transition_invalid", "Transition must be shorter than both clips", 422
            )
        pair = (left.id, right.id)
        if pair in transition_pairs:
            raise DomainError(
                "transition_duplicate", "A clip pair may have only one transition", 422
            )
        transition_pairs.add(pair)
    grouped = defaultdict(list)
    for clip in plan.clips:
        grouped[clip.track].append(clip)
    for track_clips in grouped.values():
        track_clips.sort(key=lambda clip: clip.timeline_start_frame)
        for left, right in zip(track_clips, track_clips[1:], strict=False):
            overlap = left.timeline_start_frame + left.duration_frames - right.timeline_start_frame
            if overlap > 0:
                transition_match = next(
                    (
                        t
                        for t in plan.transitions
                        if t.from_clip == left.id and t.to_clip == right.id
                    ),
                    None,
                )
                if transition_match is None or transition_match.duration_frames != overlap:
                    raise DomainError(
                        "timeline_overlap",
                        "Clip overlaps require a matching transition of equal duration",
                        422,
                    )
            elif any(t.from_clip == left.id and t.to_clip == right.id for t in plan.transitions):
                raise DomainError(
                    "transition_gap",
                    "Transition clips must overlap by the transition duration",
                    422,
                )
