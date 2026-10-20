from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdentityMixin


class Entitlement(IdentityMixin, Base):
    __tablename__ = "entitlements"
    code: Mapped[str] = mapped_column(String(80), unique=True)
    max_projects: Mapped[int] = mapped_column(default=10)
    max_storage_bytes: Mapped[int] = mapped_column(BigInteger, default=5 * 1024**3)
    max_upload_bytes: Mapped[int] = mapped_column(BigInteger, default=1024**3)
    max_render_seconds: Mapped[int] = mapped_column(default=3600)
