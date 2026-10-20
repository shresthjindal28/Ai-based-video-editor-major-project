from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DomainError
from app.db.base import now
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


async def mark_read(session: AsyncSession, user_id: UUID, notification_id: UUID):
    row = await session.scalar(select(Notification).where(Notification.id == notification_id,
                                                         Notification.user_id == user_id).with_for_update())
    if row is None:
        raise DomainError("notification_not_found", "Notification not found", 404)
    row.read_at = row.read_at or now()
    await session.flush()
    return row
