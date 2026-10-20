from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    default_aspect_ratio: Literal["16:9", "9:16", "1:1"] = "16:9"
    default_resolution: Literal["1920x1080", "1080x1920", "1080x1080"] = "1920x1080"
    default_frame_rate: Literal[24, 25, 30, 60] = 30


class ProjectUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    revision: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)


class ProjectOut(ProjectCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    owner_id: UUID
    status: str
    revision: int
    created_at: datetime
    updated_at: datetime
