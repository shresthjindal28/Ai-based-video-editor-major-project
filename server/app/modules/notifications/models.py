from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdentityMixin


class Notification(IdentityMixin, Base):
    __tablename__ = "notifications"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    job_id: Mapped[UUID] = mapped_column(ForeignKey("edit_jobs.id"))
    kind: Mapped[str] = mapped_column(String(30))
    message: Mapped[str] = mapped_column(String(500))
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (UniqueConstraint("job_id", "kind"),)
