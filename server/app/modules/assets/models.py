from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdentityMixin


class MediaAsset(IdentityMixin, Base):
    __tablename__ = "media_assets"
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="RESTRICT"), index=True
    )
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    original_filename: Mapped[str] = mapped_column(String(255))
    storage_key: Mapped[str] = mapped_column(String(500), unique=True)
    mime_type: Mapped[str] = mapped_column(String(100))
    file_size: Mapped[int] = mapped_column(BigInteger)
    checksum: Mapped[str] = mapped_column(String(64), index=True)
    media_type: Mapped[str] = mapped_column(String(20))
    duration: Mapped[float] = mapped_column(Float)
    width: Mapped[int | None]
    height: Mapped[int | None]
    fps_num: Mapped[int] = mapped_column(default=0)
    fps_den: Mapped[int] = mapped_column(default=1)
    video_codec: Mapped[str | None] = mapped_column(String(50))
    audio_codec: Mapped[str | None] = mapped_column(String(50))
    has_audio: Mapped[bool] = mapped_column(default=False)
    processing_status: Mapped[str] = mapped_column(String(20), default="pending")
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (
        Index("ix_asset_project_owner", "project_id", "owner_id", "created_at", "id"),
        CheckConstraint("file_size > 0", name="asset_positive_size"),
        CheckConstraint("duration > 0", name="asset_positive_duration"),
    )


class AssetAnalysis(IdentityMixin, Base):
    __tablename__ = "asset_analyses"
    asset_id: Mapped[UUID] = mapped_column(ForeignKey("media_assets.id"), unique=True)
    technical: Mapped[dict] = mapped_column(JSONB, default=dict)
    thumbnail_key: Mapped[str | None] = mapped_column(String(500))
    proxy_key: Mapped[str | None] = mapped_column(String(500))


class Scene(IdentityMixin, Base):
    __tablename__ = "scenes"
    asset_id: Mapped[UUID] = mapped_column(ForeignKey("media_assets.id"), index=True)
    start_frame: Mapped[int]
    end_frame: Mapped[int]
    __table_args__ = (
        CheckConstraint("end_frame > start_frame AND start_frame >= 0", name="scene_range"),
    )
