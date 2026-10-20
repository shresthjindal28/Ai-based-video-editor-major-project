from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from app.core.exceptions import DomainError
from app.db.base import now
from app.db.session import Session
from app.integrations.storage_client import storage
from app.modules.assets.models import AssetAnalysis, MediaAsset
from app.modules.jobs.runtime import check_attempt, claim, fail_attempt, lease, progress
from app.modules.jobs.service import append_event
from app.modules.rendering.media_probe import generate_proxy, generate_thumbnail


async def process_asset(asset_id: UUID, job_id: UUID) -> None:
    async with Session() as session:
        job = await claim(session, job_id)
        if job is None:
            return
        fence = job.fence
        await session.commit()
    prefix = f"derived/{asset_id.hex}/{fence}"
    keys = [f"{prefix}/thumbnail.jpg", f"{prefix}/proxy.mp4"]
    completed = False
    try:
        async with lease(job_id, fence) as cancelled:
            async with Session() as session:
                asset = await session.get(MediaAsset, asset_id)
                if asset is None or asset.deleted_at:
                    raise DomainError("asset_missing", "Source asset is unavailable", 410)
                asset.processing_status = "processing"
                source_key, media_type = asset.storage_key, asset.media_type
                await session.commit()
            source = await storage.materialize(source_key)
            if media_type == "video":
                await generate_thumbnail(source, storage.path(keys[0]), cancelled=cancelled)
                await progress(job_id, fence, 30)
                await generate_proxy(source, storage.path(keys[1]), cancelled=cancelled)
                for key in keys:
                    await storage.publish(key)
            await progress(job_id, fence, 95)
            async with Session() as session:
                job = await check_attempt(session, job_id, fence)
                asset = await session.get(MediaAsset, asset_id)
                if asset is None or asset.deleted_at:
                    raise DomainError("asset_missing", "Source asset is unavailable", 410)
                analysis = await session.scalar(select(AssetAnalysis).where(AssetAnalysis.asset_id == asset_id))
                if analysis and media_type == "video":
                    analysis.thumbnail_key, analysis.proxy_key = keys
                asset.processing_status = "ready"
                job.status, job.progress, job.completed_at = "completed", 100, now()
                await append_event(session, job, "completed", {"status": "completed", "progress": 100})
                await session.commit()
                completed = True
    except Exception as exc:
        await fail_attempt(job_id, fence, exc)
        raise
    finally:
        if not completed:
            # Attempt-specific keys keep stale cleanup away from newer work.
            for key in keys:
                storage.delete(key)
