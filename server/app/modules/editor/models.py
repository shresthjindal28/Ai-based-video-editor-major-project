from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdentityMixin


class EditRequest(IdentityMixin, Base):
    __tablename__ = "edit_requests"
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    request_type: Mapped[str] = mapped_column(String(30), default="structured")
    instructions: Mapped[dict] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(20), default="validated")


class EditVersion(IdentityMixin, Base):
    __tablename__ = "edit_versions"
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), index=True)
    version_number: Mapped[int]
    parent_version_id: Mapped[UUID | None] = mapped_column(ForeignKey("edit_versions.id"))
    timeline: Mapped[dict] = mapped_column(JSONB)
    schema_version: Mapped[str] = mapped_column(String(10), default="1")
    validation_status: Mapped[str] = mapped_column(String(20), default="valid")
    __table_args__ = (UniqueConstraint("project_id", "version_number"),)
