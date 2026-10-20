from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    project_id: UUID
    version_id: UUID | None
    job_type: str
    status: str
    progress: int
    retry_count: int
    error_code: str | None
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None


class JobEventOut(BaseModel):
    id: UUID
    job_id: UUID
    sequence: int
    event_type: str
    data: dict[str, Any]
    created_at: datetime
