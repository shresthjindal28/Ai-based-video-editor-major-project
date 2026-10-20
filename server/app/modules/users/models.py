from datetime import datetime

from sqlalchemy import (
    DateTime,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdentityMixin, now


class User(IdentityMixin, Base):
    __tablename__ = "users"
    external_subject: Mapped[str] = mapped_column(String(255), unique=True)
    email: Mapped[str | None] = mapped_column(String(320))
    display_name: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20), default="active")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)
