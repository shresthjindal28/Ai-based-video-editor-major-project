import asyncio
import os
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
from app.modules.jobs.models import EditJob, JobEvent, Outbox
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
        assert (await session.execute(text("SELECT version_num FROM alembic_version"))).scalar_one() == "0004_job_invariants"
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


async def test_real_redis_cache_stampede_invalidation_and_lock_ownership(backend):
    from app.integrations.redis_client import Cache, RedisLock, redis_client
    client = redis_client()
    prefix = f"test:{uuid4().hex}"
    cache = Cache(namespace=prefix)
    calls = 0
    async def loader():
        nonlocal calls
        calls += 1
        await asyncio.sleep(0.05)
        return {"value": calls}
    results = await asyncio.gather(*[cache.get_or_load("owner:summary", loader) for _ in range(12)])
    assert calls == 1 and all(result == {"value": 1} for result in results)
    await cache.invalidate("owner:summary")
    assert await cache.get_or_load("owner:summary", loader) == {"value": 2}
    lock = RedisLock(prefix, ttl=1)
    assert await lock.acquire()
    await asyncio.sleep(1.1)
    newer = RedisLock(prefix, ttl=10)
    assert await newer.acquire()
    await lock.release()
    assert await client.get(newer.key) == newer.token
    await newer.release()
    await client.delete(f"{prefix}:owner:summary")


async def test_outbox_failure_recovery_and_stale_job_recovery(backend, monkeypatch):
    from datetime import timedelta

    from app.db.base import now
    from app.workers.tasks import _dispatch, _recover, execute_job
    project = (await backend.client.post("/api/v1/projects", json={"name":"Outbox recovery"})).json()["id"]
    async with backend.factory() as session:
        job = EditJob(project_id=UUID(project),job_type="preview",status="pending",parameters={})
        session.add(job)
        await session.flush()
        row = Outbox(job_id=job.id)
        session.add(row)
        await session.commit()
        job_id, row_id = job.id, row.id
    def unavailable(**kwargs):
        raise ConnectionError("simulated broker outage")
    monkeypatch.setattr(execute_job,"apply_async",unavailable)
    await _dispatch()
    async with backend.factory() as session:
        row=await session.get(Outbox,row_id)
        assert row.delivered_at is None and row.attempts == 1
        row.available_at=now()-timedelta(seconds=1)
        await session.commit()
    monkeypatch.setattr(execute_job,"apply_async",lambda **kwargs:None)
    await _dispatch()
    async with backend.factory() as session:
        row=await session.get(Outbox,row_id)
        assert row.delivered_at is not None
        job=await session.get(EditJob,job_id)
        job.status="processing"
        job.heartbeat_at=now()-timedelta(seconds=get_settings().job_lease_seconds+1)
        await session.commit()
    await _recover()
    async with backend.factory() as session:
        job=await session.get(EditJob,job_id)
        assert job.status == "pending" and job.retry_count == 1 and job.fence > 0
        # This synthetic job has no version and must not be executed by the real
        # worker test below; real media handlers are covered separately.
        job.status="cancelled"
        await session.commit()


@pytest.mark.e2e
@pytest.mark.mlt
async def test_real_celery_worker_delivers_preview_from_outbox(backend):
    import sys

    from app.integrations.redis_client import redis_client
    from app.workers.celery_app import celery_app
    from app.workers.tasks import _dispatch
    if not shutil.which(get_settings().mlt_render_binary):
        pytest.skip("Configured MLT executable is unavailable")
    project, _, plan = await create_plan(backend)
    version=(await backend.client.post(f"/api/v1/projects/{project}/edits",json=plan)).json()["id"]
    response=await backend.client.post(f"/api/v1/projects/{project}/edits/{version}/preview",json={"preset":"preview"})
    assert response.status_code == 202,response.text
    job_id=response.json()["id"]
    queue=f"autocut_test_{uuid4().hex}"
    env=dict(os.environ,DATABASE_SCHEMA=backend.schema,MEDIA_STORAGE_ROOT=str(backend.root),
             STORAGE_BACKEND="local",CELERY_QUEUE=queue)
    previous_queue=celery_app.conf.task_default_queue
    previous_options=dict(celery_app.conf.broker_transport_options)
    celery_app.conf.task_default_queue=queue
    celery_app.conf.broker_transport_options={**previous_options,"global_keyprefix":queue+":"}
    log_path=backend.root/"worker.log"
    with log_path.open("wb") as log:
        process=await asyncio.create_subprocess_exec(sys.executable,"-m","celery","-A",
            "app.workers.celery_app:celery_app","worker","--pool=solo","--concurrency=1",
            "--without-gossip","--without-mingle","--without-heartbeat","--loglevel=WARNING",
            "-Q",queue,env=env,stdout=log,stderr=log)
        try:
            await _dispatch()
            deadline=asyncio.get_running_loop().time()+90
            while asyncio.get_running_loop().time()<deadline:
                result=await backend.client.get(f"/api/v1/jobs/{job_id}")
                status=result.json()["status"]
                if status in {"completed","failed","cancelled"}:
                    break
                await asyncio.sleep(1)
            assert status == "completed", result.text
            exports=(await backend.client.get(f"/api/v1/projects/{project}/exports")).json()
            downloaded=await backend.client.get(f"/api/v1/exports/{exports[0]['id']}/download")
            assert downloaded.status_code == 200 and len(downloaded.content)>1000
        finally:
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(),10)
            except TimeoutError:
                process.kill()
                await process.wait()
            celery_app.conf.task_default_queue=previous_queue
            celery_app.conf.broker_transport_options=previous_options
            # Delete only this run's namespaced broker keys.
            redis=redis_client()
            keys=[key async for key in redis.scan_iter(match=queue+":*")]
            if keys:
                await redis.delete(*keys)


async def test_resumable_upload_offsets_recovery_and_idempotent_finalization(backend):
    from app.modules.uploads import sessions
    client = backend.client
    backend.identity["user"] = backend.users[0]
    project = (await client.post("/api/v1/projects", json={"name":"Resumable upload"})).json()["id"]
    source = backend.root / "resumable-input.mp4"
    synthetic(source,"red")
    data = source.read_bytes()
    base=f"/api/v1/projects/{project}/assets/upload-sessions"
    created = await client.post(base,json={"filename":"clip.mp4","expected_size":len(data)})
    assert created.status_code == 201,created.text
    session_id=created.json()["id"]
    route=f"{base}/{session_id}"
    assert (await client.post(route+"/finalize")).status_code == 409
    assert (await client.patch(route+"/chunks",content=data[:100],headers={"Upload-Offset":"1"})).status_code == 409
    async def interrupted():
        yield b"partial bytes"
        raise ConnectionError("simulated client disconnect")
    async with backend.factory() as db:
        with pytest.raises(ConnectionError):
            await sessions.append(db,UUID(project),UUID(session_id),backend.users[0].id,0,interrupted())
        await db.rollback()
    first=await client.patch(route+"/chunks",content=data[:100],headers={"Upload-Offset":"0"})
    assert first.status_code == 200 and first.json()["offset"] == 100,first.text
    second=await client.patch(route+"/chunks",content=data[100:],headers={"Upload-Offset":"100"})
    assert second.status_code == 200 and second.json()["offset"] == len(data),second.text
    final=await client.post(route+"/finalize")
    repeated=await client.post(route+"/finalize")
    assert final.status_code == repeated.status_code == 201,(final.text,repeated.text)
    assert final.json()["id"] == repeated.json()["id"]
    backend.identity["user"] = backend.users[1]
    assert (await client.get(route)).status_code == 404
    backend.identity["user"] = backend.users[0]


async def test_durable_cleanup_removes_only_reserved_files(backend):
    from app.db.base import now
    from app.modules.storage.models import FileDeletion
    from app.modules.storage.service import cleanup
    key=f"test-cleanup/{uuid4().hex}.dat"
    path=backend.storage.path(key)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(b"temporary")
    async with backend.factory() as session:
        session.add(FileDeletion(storage_key=key,available_at=now()))
        await session.commit()
    assert await cleanup() >= 1
    assert not path.exists()
