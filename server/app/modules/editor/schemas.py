from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EditVersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    project_id: UUID
    version_number: int
    parent_version_id: UUID | None
    timeline: dict[str, Any]
    schema_version: str
    validation_status: str


class EffectKeyframe(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    frame: int = Field(ge=0)
    value: float


class EffectSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: Literal["brightness", "contrast", "saturation", "zoom", "pan", "tilt", "blur", "fade_in", "fade_out", "color", "lut"]
    parameters: dict[str, Any] = Field(default_factory=dict)
    keyframes: list[EffectKeyframe] = Field(default_factory=list, max_length=100)


class Keyframe(BaseModel):
    model_config = ConfigDict(extra="forbid")
    frame: int = Field(ge=0)
    value: float = Field(ge=0, le=4)


class ClipSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID
    asset_id: UUID
    track: int = Field(default=0, ge=0, le=7)
    source_in_frame: int = Field(ge=0)
    duration_frames: int = Field(gt=0)
    timeline_start_frame: int = Field(ge=0)
    effects: list[EffectSpec] = Field(default_factory=list, max_length=16)
    volume: float = Field(default=1.0, ge=0, le=4)
    volume_keyframes: list[Keyframe] = Field(default_factory=list, max_length=100)

    @model_validator(mode="after")
    def validate_keyframes(self):
        frames = [item.frame for item in self.volume_keyframes]
        if frames != sorted(set(frames)) or any(frame > self.duration_frames for frame in frames):
            raise ValueError("volume keyframes must be strictly ordered inside the clip")
        return self


class TransitionSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    from_clip: UUID
    to_clip: UUID
    type: Literal["cross_dissolve", "wipe", "slide"]
    duration_frames: int = Field(gt=0, le=300)


class OutputProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    width: int = Field(ge=360, le=1920, multiple_of=2)
    height: int = Field(ge=360, le=1920, multiple_of=2)
    fps_num: int = Field(default=30, gt=0, le=60000)
    fps_den: int = Field(default=1, gt=0, le=1001)
    format: Literal["mp4"] = "mp4"
    fit: Literal["contain", "cover"] = "contain"
    preset: Literal["preview", "1080p_landscape", "1080p_portrait", "1080p_square"] = (
        "1080p_landscape"
    )

    @model_validator(mode="after")
    def supported_profile(self):
        if (self.fps_num, self.fps_den) not in {(24,1),(25,1),(30,1),(50,1),(60,1),
                                               (24000,1001),(30000,1001),(60000,1001)}:
            raise ValueError("unsupported output frame rate")
        supported = {
            (1920, 1080),
            (1080, 1920),
            (1080, 1080),
            (1280, 720),
            (720, 1280),
            (640, 360),
            (360, 640),
            (640, 640),
        }
        if (self.width, self.height) not in supported:
            raise ValueError("unsupported output dimensions")
        return self


class AudioClipSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    asset_id: UUID
    source_in_frame: int = Field(default=0, ge=0)
    timeline_start_frame: int = Field(default=0, ge=0)
    duration_frames: int = Field(gt=0)
    gain: float = Field(default=1.0, ge=0, le=4)
    fade_in_frames: int = Field(default=0, ge=0)
    fade_out_frames: int = Field(default=0, ge=0)


class TitleSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(min_length=1, max_length=2000)
    start_frame: int = Field(ge=0)
    duration_frames: int = Field(gt=0)
    font_size: int = Field(default=48, ge=12, le=180)
    color: Literal["white", "black", "yellow"] = "white"
    position: Literal["top", "center", "bottom"] = "bottom"


class TimelinePlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1"] = "1"
    project_id: UUID
    output: OutputProfile
    clips: list[ClipSpec] = Field(min_length=1, max_length=500)
    audio: list[AudioClipSpec] = Field(default_factory=list, max_length=16)
    transitions: list[TransitionSpec] = Field(default_factory=list, max_length=100)
    titles: list[TitleSpec] = Field(default_factory=list, max_length=100)
    metadata: dict[str, Any] = Field(default_factory=dict)
    provenance: dict[str, Any] = Field(default_factory=dict)
