from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.assets.models import MediaAsset


async def listing(session: AsyncSession, project_id: UUID, owner_id: UUID, limit: int, offset: int):
    result = await session.scalars(
        select(MediaAsset)
        .where(
            MediaAsset.project_id == project_id,
            MediaAsset.owner_id == owner_id,
            MediaAsset.deleted_at.is_(None),
        )
        .order_by(MediaAsset.created_at, MediaAsset.id)
        .limit(limit)
        .offset(offset)
    )
    return list(result.all())
