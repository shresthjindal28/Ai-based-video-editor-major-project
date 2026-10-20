import asyncio
import json
from collections.abc import AsyncIterator
from uuid import UUID

from fastapi import APIRouter, Header, Query, Request
from fastapi.responses import StreamingResponse

from app.modules.auth.dependencies import DB, CurrentUser
from app.modules.jobs import repository, service
from app.modules.jobs.schemas import JobOut

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobOut)
async def get(job_id: UUID, db: DB, user: CurrentUser):
    return await service.require_job(db, job_id, user.id)


@router.post("/{job_id}/cancel", response_model=JobOut)
async def cancel(job_id: UUID, db: DB, user: CurrentUser):
    return await service.cancel(db, job_id, user.id)


@router.post("/{job_id}/retry", response_model=JobOut)
async def retry(
    job_id: UUID,
    db: DB,
    user: CurrentUser,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    from app.modules.auth.idempotency import begin, finish

    record = await begin(db, user.id, f"retry:{job_id}", idempotency_key, {"job_id": str(job_id)})
    if record and record.status == "completed" and record.result:
        return await service.require_job(db, UUID(record.result["job_id"]), user.id)
    job = await service.retry(db, job_id, user.id)
    finish(record, {"job_id": str(job.id)})
    await db.commit()
    return job


@router.get("/{job_id}/events")
async def events(
    job_id: UUID,
    request: Request,
    db: DB,
    user: CurrentUser,
    after: int = Query(default=0, ge=0),
    last_event_id: str | None = Header(default=None, alias="Last-Event-ID"),
):
    job = await service.require_job(db, job_id, user.id)
    cursor = max(after, int(last_event_id) if last_event_id and last_event_id.isdigit() else 0)

    async def stream() -> AsyncIterator[str]:
        nonlocal cursor
        idle = 0
        while not await request.is_disconnected():
            rows = await repository.event_history(db, job_id, cursor)
            if rows:
                for event in rows:
                    cursor = event.sequence
                    yield f"id: {event.sequence}\nevent: {event.event_type}\ndata: {json.dumps(event.data, separators=(',', ':'))}\n\n"
                idle = 0
            else:
                idle += 1
                if job.status in service.TERMINAL:
                    break
                if idle % 15 == 0:
                    yield ": heartbeat\n\n"
                await asyncio.sleep(1)
                await db.refresh(job)
        yield "event: stream_end\ndata: {}\n\n"

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache, no-transform", "X-Accel-Buffering": "no"},
    )
