from __future__ import annotations

import asyncio
import hashlib
import os
from uuid import UUID

from sqlalchemy import select

from app.core.metrics import JOBS
from app.db.base import now
from app.db.session import Session
from app.integrations.storage_client import storage
from app.modules.assets.models import MediaAsset
from app.modules.editor.models import EditVersion
from app.modules.editor.schemas import TimelinePlan
from app.modules.editor.validators import validate_plan
from app.modules.exports.models import RenderOutput
from app.modules.jobs.models import EditJob
from app.modules.jobs.service import append_event
from app.modules.notifications.models import Notification
from app.modules.projects.models import Project
from app.modules.rendering.mlt_engine import render as mlt_render
from app.modules.rendering.quality_control import verify_render


async def _cancel_monitor(job_id: UUID, fence: int, cancellation: asyncio.Event) -> None:
    while not cancellation.is_set():
        await asyncio.sleep(10)
        async with Session() as session:
            job = await session.scalar(
                select(EditJob).where(EditJob.id == job_id).with_for_update()
            )
            if job is None or job.status == "cancelling" or job.fence != fence:
                cancellation.set()
            elif job.status != "processing":
                cancellation.set()
            else:
                job.heartbeat_at = now()
                await session.commit()


async def render_job(job_id: UUID) -> None:
    async with Session() as session:
        job = await session.scalar(select(EditJob).where(EditJob.id == job_id).with_for_update())
        if job is None or job.status in {"completed", "failed", "cancelled"}:
            return
        if (
            job.status == "processing"
            and job.heartbeat_at
            and (now() - job.heartbeat_at).total_seconds() < 900
        ):
            return
        job.status, job.started_at, job.heartbeat_at = "processing", now(), now()
        job.fence += 1
        fence = job.fence
        await append_event(session, job, "processing", {"status": "processing", "progress": 0})
        version = await session.get(EditVersion, job.version_id)
        project_id = job.project_id
        if version is None:
            job.status, job.error_code, job.error_message, job.completed_at = (
                "failed",
                "version_missing",
                "Edit version not found",
                now(),
            )
            await append_event(session, job, "failed", {"error_code": job.error_code})
            await session.commit()
            return
        plan = TimelinePlan.model_validate(version.timeline)
        project = await session.get(Project, project_id)
        if project is None or project.deleted_at is not None:
            job.status, job.error_code, job.error_message, job.completed_at = (
                "failed",
                "project_missing",
                "Project is unavailable",
                now(),
            )
            await append_event(session, job, "failed", {"error_code": job.error_code})
            await session.commit()
            return
        await validate_plan(session, project.owner_id, project_id, plan)
        asset_ids = {clip.asset_id for clip in plan.clips} | {
            audio.asset_id for audio in plan.audio
        }
        assets = (
            await session.scalars(
                select(MediaAsset).where(
                    MediaAsset.id.in_(asset_ids),
                    MediaAsset.project_id == project_id,
                    MediaAsset.owner_id == project.owner_id,
                    MediaAsset.deleted_at.is_(None),
                    MediaAsset.processing_status == "ready",
                )
            )
        ).all()
        paths = {asset.id: storage.path(asset.storage_key) for asset in assets}
        if len(paths) != len(asset_ids) or not all(path.is_file() for path in paths.values()):
            raise RuntimeError("One or more source assets are missing")
        asset_rates = {
            asset.id: (asset.fps_num or plan.output.fps_num, asset.fps_den or plan.output.fps_den)
            for asset in assets
        }
        final_key = f"renders/{project_id.hex}/{job.id.hex}.mp4"
        final_path = storage.path(final_key)
        final_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        temp_path = final_path.with_name(f".{job.id.hex}.partial.mp4")
        await session.commit()

    cancellation = asyncio.Event()
    monitor = asyncio.create_task(_cancel_monitor(job_id, fence, cancellation))
    try:
        aspect = plan.output.width / plan.output.height
        preview_size = (640, 360) if aspect > 1.1 else (360, 640) if aspect < 0.9 else (640, 640)
        presets = {
            "preview": (*preview_size, plan.output.fps_num),
            "1080p_landscape": (1920, 1080, plan.output.fps_num),
            "1080p_portrait": (1080, 1920, plan.output.fps_num),
            "1080p_square": (1080, 1080, plan.output.fps_num),
        }
        width, height, _ = presets.get(job.parameters.get("preset", "preview"), presets["preview"])
        plan = plan.model_copy(
            update={
                "output": plan.output.model_copy(
                    update={
                        "width": width,
                        "height": height,
                        "preset": job.parameters.get("preset", "preview"),
                    }
                )
            }
        )
        await mlt_render(plan, paths, temp_path, asset_rates, cancellation)
        metadata = await verify_render(temp_path, plan)
        digest = hashlib.sha256()
        with temp_path.open("rb") as source:
            while chunk := source.read(1024 * 1024):
                digest.update(chunk)
        async with Session() as session:
            job = await session.scalar(
                select(EditJob).where(EditJob.id == job_id).with_for_update()
            )
            if job is None or job.status == "cancelling" or job.fence != fence:
                if job:
                    if job.status == "cancelling" and job.fence == fence:
                        job.status, job.completed_at = "cancelled", now()
                        await append_event(session, job, "cancelled", {"status": "cancelled"})
                        await session.commit()
                return
            if job.status != "processing":
                return
            # Keep promotion under the authoritative row lock so a stale worker
            # cannot replace an output produced by a newer fenced attempt.
            os.replace(temp_path, final_path)
            session.add(
                RenderOutput(
                    project_id=job.project_id,
                    version_id=job.version_id,
                    job_id=job.id,
                    storage_key=final_key,
                    format="mp4",
                    width=metadata["width"],
                    height=metadata["height"],
                    fps_num=plan.output.fps_num,
                    fps_den=plan.output.fps_den,
                    duration=metadata["duration"],
                    file_size=final_path.stat().st_size,
                    checksum=digest.hexdigest(),
                    qc_status="passed",
                )
            )
            job.status, job.progress, job.completed_at, job.heartbeat_at = (
                "completed",
                100,
                now(),
                now(),
            )
            await append_event(session, job, "completed", {"status": "completed", "progress": 100})
            project = await session.get(Project, job.project_id)
            if project:
                session.add(
                    Notification(
                        user_id=project.owner_id,
                        job_id=job.id,
                        kind="render_completed",
                        message="Your video export is ready",
                    )
                )
                from app.modules.analytics.models import UsageRecord

                session.add(UsageRecord(user_id=project.owner_id, project_id=job.project_id,
                    kind="render_seconds", amount=int(metadata["duration"]), reference=f"job:{job.id}"))
            await session.commit()
            JOBS.labels(kind=job.job_type, outcome="completed").inc()
    except Exception as exc:
        temp_path.unlink(missing_ok=True)
        final_path.unlink(missing_ok=True)
        async with Session() as session:
            job = await session.scalar(
                select(EditJob).where(EditJob.id == job_id).with_for_update()
            )
            if job and job.status not in {"completed", "cancelled"}:
                if job.status == "cancelling" or getattr(exc, "code", "") == "job_cancelled":
                    job.status, job.completed_at = "cancelled", now()
                    await append_event(session, job, "cancelled", {"status": "cancelled"})
                else:
                    job.status, job.error_code = "failed", getattr(exc, "code", "render_failed")
                    job.error_message = getattr(exc, "message", "Render failed")[:1000]
                    job.completed_at = now()
                    await append_event(
                        session,
                        job,
                        "failed",
                        {
                            "status": "failed",
                            "error_code": job.error_code,
                            "message": job.error_message,
                        },
                    )
                    project = await session.get(Project, job.project_id)
                    if project:
                        session.add(
                            Notification(
                                user_id=project.owner_id,
                                job_id=job.id,
                                kind="render_failed",
                                message="Your video export failed",
                            )
                        )
                    JOBS.labels(kind=job.job_type, outcome="failed").inc()
                await session.commit()
        raise
    finally:
        cancellation.set()
        monitor.cancel()
        try:
            await monitor
        except asyncio.CancelledError:
            pass
