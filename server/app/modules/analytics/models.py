from uuid import UUID

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdentityMixin


class UsageRecord(IdentityMixin, Base):
    __tablename__ = "usage_records"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"))
    kind: Mapped[str] = mapped_column(String(30))
    amount: Mapped[int] = mapped_column(BigInteger)
    reference: Mapped[str] = mapped_column(String(100), unique=True)
