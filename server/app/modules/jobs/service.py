from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import DomainError
from app.modules.editor.models import EditVersion
from app.modules.jobs.models import EditJob, JobEvent, Outbox
from app.modules.projects.service import require_project

ACTIVE = ("pending", "queued", "processing", "cancelling")
TERMINAL = ("completed", "failed", "cancelled")


async def append_event(session: AsyncSession, job: EditJob, kind: str, data: dict) -> JobEvent:
    job.event_sequence += 1
    event = JobEvent(job_id=job.id, sequence=job.event_sequence, event_type=kind, data=data)
    session.add(event)
    await session.flush()
    return event


async def require_job(
    session: AsyncSession, job_id: UUID, owner_id: UUID, lock: bool = False
) -> EditJob:
    from app.modules.projects.models import Project

    query = (
        select(EditJob)
        .join(Project, Project.id == EditJob.project_id)
        .where(EditJob.id == job_id, Project.owner_id == owner_id, Project.deleted_at.is_(None))
    )
    if lock:
        query = query.with_for_update(of=EditJob)
    job = await session.scalar(query)
    if job is None:
        raise DomainError("job_not_found", "Job not found", 404)
    return job


async def create_render(
    session: AsyncSession,
    project_id: UUID,
    version_id: UUID,
    owner_id: UUID,
    kind: str,
    preset: str,
) -> EditJob:
    project = await require_project(session, project_id, owner_id)
    from app.modules.projects.models import Project
    from app.modules.users.models import User

    await session.scalar(select(User.id).where(User.id == owner_id).with_for_update())
    await require_project(session, project_id, owner_id, lock=True)
    active_render_count = await session.scalar(
        select(func.count(EditJob.id))
        .join(Project, Project.id == EditJob.project_id)
        .where(Project.owner_id == owner_id, EditJob.status.in_(ACTIVE),
               EditJob.job_type.in_(["preview", "render"]))
    )
    if (active_render_count or 0) >= get_settings().max_concurrent_renders:
        raise DomainError("render_quota", "Concurrent render limit reached", 429)
    version = await session.scalar(
        select(EditVersion).where(
            EditVersion.id == version_id, EditVersion.project_id == project.id
        )
    )
    if version is None:
        raise DomainError("version_not_found", "Edit version not found", 404)
    existing = await session.scalar(
        select(EditJob)
        .where(EditJob.version_id == version.id, EditJob.status.in_(ACTIVE))
        .with_for_update()
    )
    if existing:
        if existing.job_type == kind:
            return existing
        raise DomainError(
            "render_already_active", "Another render for this edit version is active", 409
        )
    job = EditJob(
        project_id=project.id,
        version_id=version.id,
        job_type=kind,
        status="pending",
        parameters={"preset": preset},
    )
    session.add(job)
    await session.flush()
    await append_event(session, job, "created", {"job_type": kind, "status": "pending"})
    session.add(Outbox(job_id=job.id))
    await session.flush()
    return job


async def cancel(session: AsyncSession, job_id: UUID, owner_id: UUID) -> EditJob:
    job = await require_job(session, job_id, owner_id, lock=True)
    if job.status in TERMINAL:
        return job
    if job.status in {"pending", "queued"}:
        job.status, job.completed_at = "cancelled", datetime.now(UTC)
        await append_event(session, job, "cancelled", {"status": "cancelled"})
    elif job.status == "processing":
        job.status = "cancelling"
        await append_event(session, job, "cancelling", {"status": "cancelling"})
    await session.flush()
    return job


async def retry(session: AsyncSession, job_id: UUID, owner_id: UUID) -> EditJob:
    job = await require_job(session, job_id, owner_id, lock=True)
    if job.status != "failed":
        raise DomainError("job_not_retryable", "Only failed jobs can be retried", 409)
    if job.retry_count >= get_settings().max_job_retries:
        raise DomainError("retry_limit", "Job has reached its retry limit", 409)
    job.retry_count += 1
    job.status, job.progress = "pending", 0
    job.error_code = job.error_message = None
    job.started_at = job.completed_at = None
    await append_event(session, job, "retry_queued", {"retry_count": job.retry_count})
    session.add(Outbox(job_id=job.id))
    await session.flush()
    return job
