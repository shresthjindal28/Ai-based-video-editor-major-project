from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notifications.models import Notification


async def list_for_user(session: AsyncSession, user_id: UUID, limit: int, offset: int):
    rows = await session.scalars(
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc(), Notification.id)
        .limit(limit)
        .offset(offset)
    )
    return list(rows.all())
