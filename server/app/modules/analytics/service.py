from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.repository import usage


async def usage_summary(session: AsyncSession, user_id: UUID):
    return await usage(session, user_id)
