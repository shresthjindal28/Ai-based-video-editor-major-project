import asyncio
import shutil
import subprocess
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError

from app.core.config import get_settings
from app.modules.assets.processing import process_asset
from app.modules.editor.models import EditVersion
from app.modules.jobs.models import EditJob, JobEvent
from app.modules.jobs.runtime import check_attempt, claim, fail_attempt
from app.modules.rendering.media_probe import probe
from app.modules.rendering.service import render_job

pytestmark = [pytest.mark.integration, pytest.mark.asyncio(loop_scope="module")]


def synthetic(path: Path, color: str):
    subprocess.run([get_settings().ffmpeg_binary, "-v", "error", "-f", "lavfi", "-i",
        f"color=c={color}:s=320x240:r=24", "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000",
        "-t", "1", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-y", str(path)], check=True, timeout=30)


async def create_plan(backend):
    client = backend.client
    backend.identity["user"] = backend.users[0]
    response = await client.post("/api/v1/projects", json={"name": "Integration test"})
    assert response.status_code == 201, response.text
    project = response.json()["id"]
    assets = []
    for index, color in enumerate(("red", "blue")):
        source = backend.root / f"input-{uuid4().hex}.mp4"
        synthetic(source, color)
        with source.open("rb") as file:
            response = await client.post(f"/api/v1/projects/{project}/assets", files={"file": (f"input-{index}.mp4", file, "video/mp4")})
        assert response.status_code == 201, response.text
        asset_id = response.json()["id"]
        async with backend.factory() as session:
            job = await session.scalar(select(EditJob).where(EditJob.asset_id == UUID(asset_id)))
            job_id = job.id
        await process_asset(UUID(asset_id), job_id)
        assets.append(asset_id)
    plan = {"project_id": project, "output": {"width": 640, "height": 360, "fps_num": 24, "preset": "preview"},
            "clips": [{"id": str(uuid4()), "asset_id": asset_id, "source_in_frame": 0,
                       "duration_frames": 24, "timeline_start_frame": index*24} for index, asset_id in enumerate(assets)]}
    return project, assets, plan


async def test_migrations_project_crud_and_cache_invalidation(backend):
    client = backend.client
    backend.identity["user"] = backend.users[0]
    async with backend.factory() as session:
        assert (await session.execute(text("SELECT version_num FROM alembic_version"))).scalar_one() == "0002_immutable_versions"
    created = await client.post("/api/v1/projects", json={"name": "Before rename"})
    assert created.status_code == 201
    project = created.json()
    assert (await client.get("/api/v1/projects")).status_code == 200
    patched = await client.patch(f"/api/v1/projects/{project['id']}", json={"name": "After rename", "revision": project["revision"]})
    assert patched.status_code == 200, patched.text
    listing = await client.get("/api/v1/projects")
    assert any(p["name"] == "After rename" for p in listing.json())
    stale = await client.patch(f"/api/v1/projects/{project['id']}", json={"name": "Stale", "revision": project["revision"]})
    assert stale.status_code == 409
    backend.identity["user"] = backend.users[1]
    assert (await client.get(f"/api/v1/projects/{project['id']}")).status_code == 404
    backend.identity["user"] = backend.users[0]
    assert (await client.delete(f"/api/v1/projects/{project['id']}")).status_code == 204


async def test_versions_idempotency_concurrency_and_ownership(backend):
    project, assets, plan = await create_plan(backend)
    client = backend.client
    route = f"/api/v1/projects/{project}/edits"
    key = str(uuid4())
    first, second = await asyncio.gather(*[client.post(route, json=plan, headers={"Idempotency-Key": key}) for _ in range(2)])
    assert first.status_code == second.status_code == 201, (first.text, second.text)
    assert first.json()["id"] == second.json()["id"]
    changed = dict(plan, metadata={"different": True})
    assert (await client.post(route, json=changed, headers={"Idempotency-Key": key})).status_code == 409
    versions = await asyncio.gather(*[client.post(route, json=plan) for _ in range(2)])
    assert all(r.status_code == 201 for r in versions), [r.text for r in versions]
    assert len({v.json()["version_number"] for v in versions}) == 2
    async with backend.factory() as session:
        version = await session.get(EditVersion, UUID(first.json()["id"]))
        version.validation_status = "changed"
        with pytest.raises(DBAPIError):
            await session.commit()
    backend.identity["user"] = backend.users[1]
    assert (await client.get(f"{route}/{first.json()['id']}")).status_code == 404
    assert (await client.get(f"/api/v1/projects/{project}/assets/{assets[0]}/download")).status_code == 404
    backend.identity["user"] = backend.users[0]


async def test_claim_cancellation_retry_and_fencing(backend):
    project = (await backend.client.post("/api/v1/projects", json={"name": "Job race"})).json()["id"]
    async with backend.factory() as session:
        job = EditJob(project_id=UUID(project), job_type="preview", status="pending", parameters={})
        session.add(job)
        await session.commit()
        job_id = job.id
    async def compete():
        async with backend.factory() as session:
            result = await claim(session, job_id)
            await session.commit()
            return result.fence if result else None
    results = await asyncio.gather(compete(), compete())
    assert sum(value is not None for value in results) == 1
    fence = next(value for value in results if value is not None)
    await fail_attempt(job_id, fence, ConnectionError("transient"))
    async with backend.factory() as session:
        job = await session.get(EditJob, job_id)
        assert job.status == "pending" and job.retry_count == 1
        reclaimed = await claim(session, job_id)
        await session.commit()
        newer_fence = reclaimed.fence
    await fail_attempt(job_id, fence, ValueError("stale"))
    async with backend.factory() as session:
        current = await check_attempt(session, job_id, newer_fence)
        assert current.status == "processing"
    response = await backend.client.post(f"/api/v1/jobs/{job_id}/cancel")
    assert response.status_code == 200 and response.json()["status"] == "cancelling"
    await fail_attempt(job_id, newer_fence, ValueError("cancelled"))
    async with backend.factory() as session:
        current = await session.get(EditJob, job_id)
        assert current.status == "cancelled"
        events = list((await session.scalars(select(JobEvent).where(JobEvent.job_id == job_id).order_by(JobEvent.sequence))).all())
        assert [e.sequence for e in events] == list(range(1, len(events)+1))


@pytest.mark.mlt
async def test_upload_edit_render_qc_and_authorized_range_download(backend):
    if not shutil.which(get_settings().mlt_render_binary):
        pytest.skip("Configured MLT executable is unavailable")
    project, assets, plan = await create_plan(backend)
    client = backend.client
    response = await client.post(f"/api/v1/projects/{project}/edits", json=plan)
    assert response.status_code == 201, response.text
    version = response.json()["id"]
    route = f"/api/v1/projects/{project}/edits/{version}/preview"
    jobs = await asyncio.gather(*[client.post(route, json={"preset": "preview"}) for _ in range(2)])
    assert jobs[0].status_code == jobs[1].status_code == 202, [r.text for r in jobs]
    assert jobs[0].json()["id"] == jobs[1].json()["id"]
    job_id = jobs[0].json()["id"]
    assert (await client.delete(f"/api/v1/projects/{project}/assets/{assets[0]}")).status_code == 409
    await render_job(UUID(job_id))
    result = await client.get(f"/api/v1/jobs/{job_id}")
    assert result.json()["status"] == "completed", result.text
    outputs = (await client.get(f"/api/v1/projects/{project}/exports")).json()
    assert len(outputs) == 1
    export_id = outputs[0]["id"]
    response = await client.get(f"/api/v1/exports/{export_id}/download", headers={"Range": "bytes=0-127"})
    assert response.status_code == 206 and len(response.content) == 128
    response = await client.get(f"/api/v1/exports/{export_id}/download")
    final = backend.root / "downloaded.mp4"
    final.write_bytes(response.content)
    metadata = await probe(final)
    assert metadata["width"] == 640 and metadata["has_audio"]
    backend.identity["user"] = backend.users[1]
    for path in (f"/api/v1/jobs/{job_id}", f"/api/v1/exports/{export_id}", f"/api/v1/exports/{export_id}/download"):
        assert (await client.get(path)).status_code == 404
    backend.identity["user"] = backend.users[0]
