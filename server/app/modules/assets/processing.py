from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from app.db.base import now
from app.db.session import Session
from app.integrations.storage_client import storage
from app.modules.assets.models import AssetAnalysis, MediaAsset
from app.modules.jobs.models import EditJob
from app.modules.jobs.service import append_event
from app.modules.rendering.media_probe import generate_proxy, generate_thumbnail


async def process_asset(asset_id: UUID, job_id: UUID) -> None:
    async with Session() as session:
        job = await session.scalar(select(EditJob).where(EditJob.id == job_id).with_for_update())
        asset = await session.scalar(
            select(MediaAsset).where(MediaAsset.id == asset_id).with_for_update()
        )
        if job is None or asset is None or job.status in {"completed", "failed", "cancelled"}:
            return
        if (
            job.status == "processing"
            and job.heartbeat_at
            and (now() - job.heartbeat_at).total_seconds() < 600
        ):
            return
        job.status, job.started_at, job.heartbeat_at = "processing", now(), now()
        job.fence += 1
        fence = job.fence
        asset.processing_status = "processing"
        source = storage.path(asset.storage_key)
        thumbnail_key = f"derived/{asset.id.hex}/thumbnail.jpg"
        proxy_key = f"derived/{asset.id.hex}/proxy.mp4"
        thumbnail, proxy = storage.path(thumbnail_key), storage.path(proxy_key)
        await session.commit()
    try:
        if not source.is_file():
            raise FileNotFoundError("Source upload is unavailable")
        if asset.media_type == "video":
            await generate_thumbnail(source, thumbnail)
            await generate_proxy(source, proxy)
        async with Session() as session:
            job = await session.scalar(
                select(EditJob).where(EditJob.id == job_id).with_for_update()
            )
            asset = await session.scalar(
                select(MediaAsset).where(MediaAsset.id == asset_id).with_for_update()
            )
            if job is None or asset is None or job.status == "cancelling" or job.fence != fence:
                thumbnail.unlink(missing_ok=True)
                proxy.unlink(missing_ok=True)
                if asset and job and job.status == "cancelling":
                    asset.processing_status = "cancelled"
                    job.status, job.completed_at = "cancelled", now()
                    await append_event(session, job, "cancelled", {"status": "cancelled"})
                    await session.commit()
                return
            analysis = await session.scalar(
                select(AssetAnalysis).where(AssetAnalysis.asset_id == asset.id)
            )
            if analysis:
                analysis.thumbnail_key = thumbnail_key if thumbnail.exists() else None
                analysis.proxy_key = proxy_key if proxy.exists() else None
            asset.processing_status = "ready"
            job.status, job.progress, job.completed_at, job.heartbeat_at = (
                "completed",
                100,
                now(),
                now(),
            )
            await append_event(session, job, "completed", {"status": "completed", "progress": 100})
            await session.commit()
    except Exception as exc:
        thumbnail.unlink(missing_ok=True)
        proxy.unlink(missing_ok=True)
        async with Session() as session:
            job = await session.get(EditJob, job_id)
            asset = await session.get(MediaAsset, asset_id)
            if job and job.status not in {"completed", "cancelled"}:
                job.status, job.error_code, job.error_message, job.completed_at = (
                    "failed",
                    "asset_processing_failed",
                    type(exc).__name__,
                    now(),
                )
                await append_event(session, job, "failed", {"error_code": job.error_code})
            if asset:
                asset.processing_status = "failed"
            await session.commit()
        raise
