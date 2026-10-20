from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.editor.models import EditVersion


async def next_version(session: AsyncSession, project_id: UUID) -> int:
    current = await session.scalar(
        select(func.max(EditVersion.version_number)).where(EditVersion.project_id == project_id)
    )
    return (current or 0) + 1


async def listing(session: AsyncSession, project_id: UUID, limit: int, offset: int):
    rows = await session.scalars(
        select(EditVersion)
        .where(EditVersion.project_id == project_id)
        .order_by(EditVersion.version_number.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(rows.all())
