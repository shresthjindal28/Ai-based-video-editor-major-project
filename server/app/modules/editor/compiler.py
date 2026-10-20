from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import ceil
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
    effects: tuple[dict, ...]


@dataclass(frozen=True)
class CompiledTimeline:
    width: int
    height: int
    fps_num: int
    fps_den: int
    duration_frames: int
    clips: tuple[CompiledClip, ...]
    transitions: tuple[dict, ...]
    audio: tuple[dict, ...]
    titles: tuple[dict, ...]


def compile_plan(plan: TimelinePlan, source_rates: dict[UUID, tuple[int, int]] | None = None) -> CompiledTimeline:
    """Pure deterministic compilation from validated frame data to render operations."""
    clips = tuple(
        sorted(
            (
                CompiledClip(
                    id=clip.id,
                    asset_id=clip.asset_id,
                    track=clip.track,
                    source_in_frame=clip.source_in_frame,
                    source_out_frame=clip.source_in_frame + ceil(
                        Fraction(clip.duration_frames * plan.output.fps_den, plan.output.fps_num)
                        * Fraction(*(source_rates or {}).get(clip.asset_id, (plan.output.fps_num, plan.output.fps_den)))
                    ) - 1,
                    timeline_start_frame=clip.timeline_start_frame,
                    timeline_end_frame=clip.timeline_start_frame + clip.duration_frames - 1,
                    effect_ids=tuple(effect.id for effect in clip.effects),
                    effects=tuple(effect.model_dump(mode="json") for effect in clip.effects),
                )
                for clip in plan.clips
            ),
            key=lambda item: (item.track, item.timeline_start_frame, str(item.id)),
        )
    )
    end = max([item.timeline_end_frame for item in clips] +
              [audio.timeline_start_frame+audio.duration_frames-1 for audio in plan.audio])
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
        tuple(audio.model_dump(mode="json") for audio in plan.audio),
        tuple(title.model_dump(mode="json") for title in plan.titles),
    )
