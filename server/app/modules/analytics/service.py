from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.redis_client import Cache
from app.modules.analytics.repository import usage


async def usage_summary(session: AsyncSession, user_id: UUID):
    return await Cache().get_or_load(f"usage:{user_id}:summary", lambda: usage(session, user_id), ttl=30)
