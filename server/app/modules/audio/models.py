from uuid import UUID

from sqlalchemy import JSON, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdentityMixin


class AudioTrack(IdentityMixin, Base):
    __tablename__ = "audio_tracks"
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    asset_id: Mapped[UUID] = mapped_column(ForeignKey("media_assets.id", ondelete="RESTRICT"))
    version_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("edit_versions.id", ondelete="CASCADE")
    )
    track_number: Mapped[int] = mapped_column(default=0)
    gain: Mapped[float] = mapped_column(default=1.0)
    fade_in_frames: Mapped[int] = mapped_column(default=0)
    fade_out_frames: Mapped[int] = mapped_column(default=0)
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
    __table_args__ = (
        CheckConstraint("gain >= 0 AND gain <= 4", name="audio_gain_range"),
        CheckConstraint(
            "fade_in_frames >= 0 AND fade_out_frames >= 0", name="audio_fades_nonnegative"
        ),
    )
