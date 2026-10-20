from __future__ import annotations

import hashlib
import os
from uuid import UUID

import anyio
from sqlalchemy import select

from app.core.exceptions import DomainError
from app.core.metrics import JOBS
from app.db.base import now
from app.db.session import Session
from app.integrations.storage_client import storage
from app.modules.analytics.models import UsageRecord
from app.modules.assets.models import MediaAsset
from app.modules.editor.models import EditVersion
from app.modules.editor.schemas import TimelinePlan
from app.modules.editor.validators import validate_plan
from app.modules.exports.models import RenderOutput
from app.modules.jobs.runtime import check_attempt, claim, fail_attempt, lease, progress
from app.modules.jobs.service import append_event
from app.modules.notifications.models import Notification
from app.modules.projects.models import Project
from app.modules.rendering.mlt_engine import render as mlt_render
from app.modules.rendering.quality_control import verify_render
from app.modules.storage.service import keep, reserve


def checksum(path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


async def render_job(job_id: UUID) -> None:
    async with Session() as session:
        job = await claim(session, job_id)
        if job is None:
            return
        fence, project_id, version_id = job.fence, job.project_id, job.version_id
        preset = job.parameters.get("preset", "preview")
        await session.commit()
    final_key = f"renders/{project_id.hex}/{job_id.hex}/{fence}.mp4"
    final_path = storage.path(final_key)
    final_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temp_path = final_path.with_suffix(".partial.mp4")
    completed = False
    try:
        await reserve(final_key)
        async with lease(job_id, fence) as cancelled:
            async with Session() as session:
                project = await session.get(Project, project_id)
                version = await session.get(EditVersion, version_id)
                if project is None or project.deleted_at or version is None:
                    raise DomainError("render_source_missing", "Project or edit version is unavailable", 410)
                plan = TimelinePlan.model_validate(version.timeline)
                await validate_plan(session, project.owner_id, project_id, plan)
                asset_ids = {clip.asset_id for clip in plan.clips} | {a.asset_id for a in plan.audio}
                assets = list((await session.scalars(select(MediaAsset).where(MediaAsset.id.in_(asset_ids)))).all())
                owner_id = project.owner_id
            paths = {asset.id: await storage.materialize(asset.storage_key) for asset in assets}
            rates = {asset.id: (asset.fps_num or plan.output.fps_num, asset.fps_den or plan.output.fps_den) for asset in assets}
            aspect = plan.output.width / plan.output.height
            preview = (640, 360) if aspect > 1.1 else (360, 640) if aspect < 0.9 else (640, 640)
            sizes = {"preview": preview, "1080p_landscape": (1920, 1080),
                     "1080p_portrait": (1080, 1920), "1080p_square": (1080, 1080)}
            if preset not in sizes:
                raise DomainError("invalid_preset", "Unsupported render preset", 422)
            width, height = sizes[preset]
            output = plan.output.model_copy(update={"width": width, "height": height, "preset": preset})
            plan = plan.model_copy(update={"output": output})
            await progress(job_id, fence, 10)
            await mlt_render(plan, paths, temp_path, rates, cancelled)
            await progress(job_id, fence, 85)
            metadata = await verify_render(temp_path, plan)
            digest = await anyio.to_thread.run_sync(checksum, temp_path)
            size = temp_path.stat().st_size
            os.replace(temp_path, final_path)
            await storage.publish(final_key)
            async with Session() as session:
                job = await check_attempt(session, job_id, fence)
                session.add(RenderOutput(project_id=project_id, version_id=version_id,
                    job_id=job_id, storage_key=final_key, format="mp4", width=width, height=height,
                    fps_num=output.fps_num, fps_den=output.fps_den, duration=metadata["duration"],
                    file_size=size, checksum=digest, qc_status="passed"))
                await keep(session, [final_key])
                job.status, job.progress, job.completed_at, job.heartbeat_at = "completed", 100, now(), now()
                await append_event(session, job, "completed", {"status": "completed", "progress": 100})
                session.add(Notification(user_id=owner_id, job_id=job_id, kind="render_completed", message="Your video export is ready"))
                session.add(UsageRecord(user_id=owner_id, project_id=project_id, kind="render_seconds",
                    amount=int(metadata["duration"]), reference=f"job:{job_id}"))
                await session.commit()
                completed = True
                JOBS.labels(kind=job.job_type, outcome="completed").inc()
    except Exception as exc:
        await fail_attempt(job_id, fence, exc)
        raise
    finally:
        temp_path.unlink(missing_ok=True)
        if not completed:
            final_path.unlink(missing_ok=True)
