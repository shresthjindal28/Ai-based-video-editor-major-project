from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.jobs.models import JobEvent


async def event_history(session: AsyncSession, job_id: UUID, after: int = 0, limit: int = 500):
    rows = await session.scalars(
        select(JobEvent)
        .where(JobEvent.job_id == job_id, JobEvent.sequence > after)
        .order_by(JobEvent.sequence)
        .limit(limit)
    )
    return list(rows.all())
