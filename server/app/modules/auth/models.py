from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdentityMixin


class IdempotencyRecord(IdentityMixin, Base):
    __tablename__ = "idempotency_records"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    scope: Mapped[str] = mapped_column(String(200))
    key: Mapped[str] = mapped_column(String(200))
    fingerprint: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(20), default="processing")
    result: Mapped[dict | None] = mapped_column(JSONB)
    __table_args__ = (UniqueConstraint("user_id", "scope", "key"),)
