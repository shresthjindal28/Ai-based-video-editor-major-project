import asyncio
import logging
import random
from datetime import timedelta
from uuid import UUID

from sqlalchemy import select

from app.core.config import get_settings
from app.db.base import now
from app.db.session import Session
from app.modules.assets.processing import process_asset
from app.modules.jobs.models import EditJob, Outbox
from app.modules.jobs.service import append_event
from app.modules.rendering.service import render_job
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)
_runner: asyncio.Runner | None = None


def run_async(operation):
    """Reuse one event loop per prefork process for asyncpg/Redis pools."""
    global _runner
    if _runner is None:
        _runner = asyncio.Runner()
    return _runner.run(operation)


@celery_app.task(
    name="app.workers.tasks.execute_job", bind=True, acks_late=True, reject_on_worker_lost=True
)
def execute_job(self, job_id: str) -> None:
    run_async(_execute(UUID(job_id)))


async def _execute(job_id: UUID) -> None:
    async with Session() as session:
        job = await session.get(EditJob, job_id)
        if job is None:
            return
        asset_id, job_type = job.asset_id, job.job_type
    try:
        if job_type == "asset_processing" and asset_id:
            await process_asset(asset_id, job_id)
        else:
            await render_job(job_id)
    except Exception:
        # Handlers persist failure under their own fencing token. An unowned
        # exception must never overwrite a newer worker's result.
        logger.exception("background attempt failed", extra={"job_id": str(job_id)})
        raise


@celery_app.task(name="app.workers.tasks.dispatch_outbox", ignore_result=True)
def dispatch_outbox() -> int:
    return run_async(_dispatch())


async def _dispatch() -> int:
    dispatched = 0
    async with Session() as session:
        rows = list(
            (
                await session.scalars(
                    select(Outbox)
                    .where(Outbox.delivered_at.is_(None), Outbox.available_at <= now())
                    .order_by(Outbox.created_at)
                    .limit(50)
                    .with_for_update(skip_locked=True)
                )
            ).all()
        )
        for row in rows:
            job = await session.scalar(select(EditJob).where(EditJob.id == row.job_id).with_for_update())
            if job is None or job.status not in {"pending", "queued"}:
                row.delivered_at = now()
                continue
            try:
                execute_job.apply_async(args=[str(job.id)], task_id=str(job.id))
                row.delivered_at = now()
                row.attempts += 1
                job.status = "queued" if job.status == "pending" else job.status
                job.celery_task_id = str(job.id)
                job.heartbeat_at = now()
                await append_event(session, job, "queued", {"status": job.status})
                dispatched += 1
            except Exception as exc:
                row.attempts += 1
                row.last_error = type(exc).__name__
                if row.attempts >= get_settings().max_outbox_attempts:
                    row.delivered_at = now()
                    job.status, job.error_code, job.error_message, job.completed_at = (
                        "failed",
                        "dispatch_failed",
                        "Background worker queue is unavailable",
                        now(),
                    )
                    await append_event(session, job, "failed", {"error_code": job.error_code})
                else:
                    row.available_at = now() + timedelta(
                        seconds=min(300, 2 ** min(row.attempts, 8)) + random.randint(0, 5)
                    )
        await session.commit()
    return dispatched


@celery_app.task(name="app.workers.tasks.recover_stale_jobs", ignore_result=True)
def recover_stale_jobs() -> int:
    return run_async(_recover())


async def _recover() -> int:
    recovered = 0
    # Rendering has an explicit heartbeat; this window exceeds the configured
    # subprocess timeout so a live but slow render is never reclaimed.
    stale_before = now() - timedelta(seconds=get_settings().job_lease_seconds)
    async with Session() as session:
        rows = list(
            (
                await session.scalars(
                    select(EditJob)
                    .where(EditJob.status.in_(["processing", "cancelling"]), EditJob.heartbeat_at < stale_before)
                    .limit(100)
                    .with_for_update(skip_locked=True)
                )
            ).all()
        )
        for job in rows:
            if job.status == "cancelling":
                job.status, job.completed_at = "cancelled", now()
                job.fence += 1
                await append_event(session, job, "cancelled", {"status": "cancelled"})
            elif job.retry_count >= get_settings().max_job_retries:
                job.status, job.error_code, job.error_message, job.completed_at = (
                    "failed",
                    "worker_lost",
                    "Worker stopped before completing the job",
                    now(),
                )
                await append_event(session, job, "failed", {"error_code": job.error_code})
            else:
                job.retry_count += 1
                job.status, job.progress, job.heartbeat_at = "pending", 0, None
                job.fence += 1
                session.add(Outbox(job_id=job.id))
                await append_event(session, job, "recovered", {"retry_count": job.retry_count})
            recovered += 1
        queued = list(
            (
                await session.scalars(
                    select(EditJob)
                    .where(EditJob.status == "queued", EditJob.heartbeat_at < stale_before)
                    .limit(100)
                    .with_for_update(skip_locked=True)
                )
            ).all()
        )
        for job in queued:
            job.status, job.heartbeat_at = "pending", None
            job.fence += 1
            session.add(Outbox(job_id=job.id))
            await append_event(session, job, "redispatched", {"status": "pending"})
            recovered += 1
        await session.commit()
    return recovered
