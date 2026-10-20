"""Database-fenced worker attempts and cooperative leases.

Lock ordering: job, then asset. Request creation locks user, then project.
Only recovery may reclaim a processing job; duplicate delivery cannot claim it.
"""
from __future__ import annotations

import asyncio
import random
from contextlib import asynccontextmanager
from datetime import timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import ProcessError
from app.db.base import now
from app.db.session import Session
from app.modules.jobs.models import EditJob, Outbox
from app.modules.jobs.service import append_event


async def claim(session: AsyncSession, job_id: UUID) -> EditJob | None:
    job = await session.scalar(select(EditJob).where(EditJob.id == job_id).with_for_update())
    if job is None or job.status not in {"pending", "queued"}:
        return None
    job.status, job.started_at, job.heartbeat_at = "processing", now(), now()
    job.fence += 1
    job.progress = 1
    await append_event(session, job, "processing", {"status": job.status, "progress": 1})
    return job


async def check_attempt(session: AsyncSession, job_id: UUID, fence: int) -> EditJob:
    job = await session.scalar(select(EditJob).where(EditJob.id == job_id).with_for_update())
    if job is None or job.fence != fence or job.status != "processing":
        raise ProcessError("job_cancelled", "Job attempt is no longer active", 409)
    return job


async def progress(job_id: UUID, fence: int, value: int) -> None:
    async with Session() as session:
        job = await check_attempt(session, job_id, fence)
        value = max(job.progress, min(99, value))
        if value > job.progress:
            job.progress = value
            await append_event(session, job, "progress", {"status": "processing", "progress": value})
        job.heartbeat_at = now()
        await session.commit()


def is_transient(exc: Exception) -> bool:
    if isinstance(exc, (ConnectionError, TimeoutError)):
        return True
    if isinstance(exc, DBAPIError):
        return exc.connection_invalidated or getattr(exc.orig, "sqlstate", None) in {"40001", "40P01", "08006", "08001"}
    return type(exc).__name__ in {"EndpointConnectionError", "ReadTimeoutError", "ConnectionClosedError"}


async def fail_attempt(job_id: UUID, fence: int, exc: Exception) -> None:
    from app.modules.notifications.models import Notification
    from app.modules.projects.models import Project

    async with Session() as session:
        job = await session.scalar(select(EditJob).where(EditJob.id == job_id).with_for_update())
        if job is None or job.fence != fence or job.status not in {"processing", "cancelling"}:
            return
        if job.status == "cancelling" or getattr(exc, "code", "") == "job_cancelled":
            job.status, job.completed_at = "cancelled", now()
        elif is_transient(exc) and job.retry_count < get_settings().max_job_retries:
            job.retry_count += 1
            job.status, job.progress, job.heartbeat_at = "pending", 0, None
            delay = min(300, 2 ** job.retry_count) + random.uniform(0, 3)
            session.add(Outbox(job_id=job.id, available_at=now() + timedelta(seconds=delay)))
        else:
            job.status, job.completed_at = "failed", now()
            project = await session.get(Project, job.project_id)
            if project:
                session.add(Notification(user_id=project.owner_id, job_id=job.id,
                    kind="job_failed", message="Background media processing failed"))
        job.error_code = getattr(exc, "code", "processing_failed")
        job.error_message = getattr(exc, "message", "Background processing failed")[:1000]
        await append_event(session, job, job.status, {
            "status": job.status, "error_code": job.error_code,
            "message": job.error_message, "retry_count": job.retry_count,
        })
        await session.commit()


@asynccontextmanager
async def lease(job_id: UUID, fence: int):
    cancelled = asyncio.Event()

    async def monitor() -> None:
        while True:
            await asyncio.sleep(max(1, min(10, get_settings().job_lease_seconds / 3)))
            try:
                async with Session() as session:
                    job = await check_attempt(session, job_id, fence)
                    job.heartbeat_at = now()
                    await session.commit()
            except Exception:
                # Losing the authoritative lease stops the process; retry and
                # recovery must verify the persisted fencing token.
                cancelled.set()
                return

    monitor_task = asyncio.create_task(monitor())
    try:
        yield cancelled
    finally:
        cancelled.set()
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
