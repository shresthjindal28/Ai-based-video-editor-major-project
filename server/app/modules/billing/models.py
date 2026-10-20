from uuid import UUID

from sqlalchemy import BigInteger, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdentityMixin


class UsageLedger(IdentityMixin, Base):
    __tablename__ = "usage_ledger"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    period: Mapped[str] = mapped_column(String(7))
    storage_bytes: Mapped[int] = mapped_column(BigInteger, default=0)
    rendered_seconds: Mapped[int] = mapped_column(BigInteger, default=0)
    __table_args__ = (UniqueConstraint("user_id", "period"),)
