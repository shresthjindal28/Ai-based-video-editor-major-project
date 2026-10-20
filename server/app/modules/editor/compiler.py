from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.modules.editor.schemas import TimelinePlan


@dataclass(frozen=True)
class CompiledClip:
    id: UUID
    asset_id: UUID
    track: int
    source_in_frame: int
    source_out_frame: int
    timeline_start_frame: int
    timeline_end_frame: int
    effect_ids: tuple[str, ...]


@dataclass(frozen=True)
class CompiledTimeline:
    width: int
    height: int
    fps_num: int
    fps_den: int
    duration_frames: int
    clips: tuple[CompiledClip, ...]
    transitions: tuple[dict, ...]


def compile_plan(plan: TimelinePlan) -> CompiledTimeline:
    """Pure deterministic compilation from validated frame data to render operations."""
    clips = tuple(
        sorted(
            (
                CompiledClip(
                    id=clip.id,
                    asset_id=clip.asset_id,
                    track=clip.track,
                    source_in_frame=clip.source_in_frame,
                    source_out_frame=clip.source_in_frame + clip.duration_frames - 1,
                    timeline_start_frame=clip.timeline_start_frame,
                    timeline_end_frame=clip.timeline_start_frame + clip.duration_frames - 1,
                    effect_ids=tuple(effect.id for effect in clip.effects),
                )
                for clip in plan.clips
            ),
            key=lambda item: (item.track, item.timeline_start_frame, str(item.id)),
        )
    )
    end = max(item.timeline_end_frame for item in clips)
    transitions = tuple(
        sorted(
            (item.model_dump(mode="json") for item in plan.transitions),
            key=lambda item: (item["from_clip"], item["to_clip"]),
        )
    )
    return CompiledTimeline(
        plan.output.width,
        plan.output.height,
        plan.output.fps_num,
        plan.output.fps_den,
        end + 1,
        clips,
        transitions,
    )
