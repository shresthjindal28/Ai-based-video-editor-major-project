from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdentityMixin, now


class FileDeletion(IdentityMixin, Base):
    __tablename__ = "file_deletions"
    storage_key: Mapped[str] = mapped_column(String(500), unique=True)
    attempts: Mapped[int] = mapped_column(default=0)
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)
    last_error: Mapped[str | None] = mapped_column(String(100))
