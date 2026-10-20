from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdentityMixin, now


class Project(IdentityMixin, Base):
    __tablename__ = "projects"
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="active")
    default_aspect_ratio: Mapped[str] = mapped_column(String(10), default="16:9")
    default_resolution: Mapped[str] = mapped_column(String(20), default="1920x1080")
    default_frame_rate: Mapped[int] = mapped_column(default=30)
    revision: Mapped[int] = mapped_column(default=1)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (Index("ix_project_owner_created", "owner_id", "created_at", "id"),)
