from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdentityMixin, now


class EditJob(IdentityMixin, Base):
    __tablename__ = "edit_jobs"
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), index=True)
    version_id: Mapped[UUID | None] = mapped_column(ForeignKey("edit_versions.id"))
    asset_id: Mapped[UUID | None] = mapped_column(ForeignKey("media_assets.id"))
    job_type: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    progress: Mapped[int] = mapped_column(default=0)
    celery_task_id: Mapped[str | None] = mapped_column(String(100))
    retry_count: Mapped[int] = mapped_column(default=0)
    error_code: Mapped[str | None] = mapped_column(String(100))
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fence: Mapped[int] = mapped_column(default=0)
    event_sequence: Mapped[int] = mapped_column(default=0)
    parameters: Mapped[dict] = mapped_column(JSONB, default=dict)
    __table_args__ = (
        Index(
            "uq_active_version_render",
            "version_id",
            unique=True,
            postgresql_where=text(
                "status IN ('pending','queued','processing','cancelling') AND version_id IS NOT NULL"
            ),
        ),
    )


class JobEvent(IdentityMixin, Base):
    __tablename__ = "job_events"
    job_id: Mapped[UUID] = mapped_column(ForeignKey("edit_jobs.id"), index=True)
    sequence: Mapped[int]
    event_type: Mapped[str] = mapped_column(String(40))
    data: Mapped[dict] = mapped_column(JSONB)
    __table_args__ = (UniqueConstraint("job_id", "sequence"),)


class Outbox(IdentityMixin, Base):
    __tablename__ = "outbox"
    job_id: Mapped[UUID] = mapped_column(ForeignKey("edit_jobs.id"), index=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    attempts: Mapped[int] = mapped_column(default=0)
    last_error: Mapped[str | None] = mapped_column(String(100))
    __table_args__ = (Index("ix_outbox_dispatch", "delivered_at", "available_at", "created_at"),)
