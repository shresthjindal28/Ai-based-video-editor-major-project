from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdentityMixin


class TimelineItem(IdentityMixin, Base):
    __tablename__ = "timeline_items"
    version_id: Mapped[UUID] = mapped_column(ForeignKey("edit_versions.id"), index=True)
    asset_id: Mapped[UUID] = mapped_column(ForeignKey("media_assets.id"), index=True)
    track: Mapped[int]
    start_frame: Mapped[int]
    duration_frames: Mapped[int]
