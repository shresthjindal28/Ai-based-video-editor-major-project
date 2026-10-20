# AutoCut main backend

This directory contains the Python resource server for AutoCut AI. It owns users synchronized from Better Auth, projects, source media, immutable edit plans, render jobs, and exports. The AI worker and frontend remain separate services.

## Local requirements

- Python 3.12 or newer and `uv`
- PostgreSQL
- Redis
- FFmpeg and ffprobe
- MLT with the `melt` CLI and its `avformat` consumer, plus H.264/AAC codecs

The backend does not start containers. This machine has a minimal MLT 7.42 build under `server/.local/mlt`; `server/.env` points at its renderer. On another machine, install MLT with avformat, XML and core modules, then set `MLT_RENDER_BINARY`. `/health/ready` checks PostgreSQL, Redis, media executables, authentication configuration and storage configuration. Protected routes fail closed unless Better Auth JWT/JWKS settings are configured.

## Configure and run

Use `.env.example` as the configuration reference. The local `.env` already contains the PostgreSQL/Redis connection settings supplied for this project; do not overwrite it or commit it. Fill in your own R2 and authentication settings as needed. `AUTH_ISSUER`, `AUTH_AUDIENCE`, `AUTH_JWKS_URL` and R2 credentials are intentionally blank in the example file. The backend never accepts identity headers or an unverified user ID.

```bash
cd server
uv sync --group dev
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000
```

Run a Celery worker and its independent scheduler in separate terminals:

```bash
cd server
uv run celery -A app.workers.celery_app:celery_app worker --loglevel=INFO
uv run celery -A app.workers.celery_app:celery_app beat --loglevel=INFO
```

The outbox dispatcher publishes committed jobs to Celery. PostgreSQL job rows and events are authoritative; Redis is used for delivery, coordination, rate limits, and read-through cache data. Delivery is at least once, and job handlers use row locks and fencing checks to discard duplicate or stale work.

API documentation is served at `http://localhost:8000/docs`; the OpenAPI schema is at `/openapi.json`. Health endpoints are `/health` and `/health/ready`. Prometheus metrics are available at `/metrics`.

## Better Auth token contract

Use Better Auth's JWT plugin in the Next.js service and its client plugin. The plugin's JWKS-verifiable token endpoint is distinct from Better Auth's session cookie. Configure the JWT plugin with the same issuer and audience values supplied to the Python service, publish its JWKS endpoint, and pass the resulting token to the backend as `Authorization: Bearer <token>`. The documented default JWKS path is `/api/auth/jwks`; set `AUTH_JWKS_URL` to the full public URL. The JWT plugin can use a custom JWKS path if both services agree on it.

An illustrative Better Auth server configuration is:

```ts
import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";

export const auth = betterAuth({
  plugins: [
    jwt({
      jwks: { keyPairConfig: { alg: "EdDSA", crv: "Ed25519" } },
      jwt: {
        issuer: process.env.AUTH_ISSUER!,
        audience: process.env.AUTH_AUDIENCE!,
        expirationTime: "15m",
        getSubject: (session) => session.user.id,
        definePayload: ({ user }) => ({ email: user.email, name: user.name }),
      },
    }),
  ],
});
```

The frontend can use `jwtClient()` and `authClient.token()` to obtain the API token. Keep tokens short-lived and use HTTPS outside local development. The backend accepts only `EdDSA`, `RS256`, or `ES256`, and checks `iss`, `aud`, `exp`, `iat`, and `sub` before synchronizing a user. Better Auth's JWT plugin documentation: [JWT plugin](https://better-auth.com/docs/plugins/jwt).

## Editing workflow

1. `POST /api/v1/projects` creates an owned project.
2. `POST /api/v1/projects/{project_id}/assets` streams one media file into private staging, computes SHA-256, probes it with ffprobe, publishes it through the selected storage backend, then queues thumbnail/proxy preparation. The asset is editable once its processing status is `ready`.
3. `POST /api/v1/projects/{project_id}/edits/validate` validates a version 1 frame-based timeline plan.
4. `POST /api/v1/projects/{project_id}/edits` creates an immutable version. Supply an `Idempotency-Key` for retry-safe creation.
5. `POST /api/v1/projects/{project_id}/edits/{version_id}/preview` or `/render` queues a Celery job through the PostgreSQL outbox.
6. Poll `GET /api/v1/jobs/{job_id}` or stream persisted events from `/api/v1/jobs/{job_id}/events`. Download a completed output with `/api/v1/exports/{export_id}/download`.

Timeline times use integer frames. `source_in_frame` is in the source asset's probed frame rate; `duration_frames`, `timeline_start_frame`, and transition durations use the selected output profile frame rate. Source ranges are converted through rational frame rates before rendering. Unsupported effects, invalid source ranges, and unauthorized assets are rejected.

An example plan (replace project and asset UUIDs with values returned by the API):

```json
{
  "schema_version": "1",
  "project_id": "PROJECT_UUID",
  "output": {"width": 1920, "height": 1080, "fps_num": 30, "fps_den": 1, "format": "mp4", "preset": "1080p_landscape"},
  "clips": [
    {"id": "CLIP_UUID", "asset_id": "ASSET_UUID", "track": 0, "source_in_frame": 0, "duration_frames": 120, "timeline_start_frame": 0,
     "effects": [{"id": "saturation", "parameters": {"value": 1.1}}], "volume": 1.0, "volume_keyframes": []}
  ],
  "audio": [],
  "transitions": [],
  "metadata": {},
  "provenance": {"request": "hand-authored structured plan"}
}
```

For example, submit the plan to `/api/v1/projects/PROJECT_UUID/edits`, then submit `{ "preset": "preview" }` to the preview route. Include a valid Better Auth bearer token and an idempotency key on side-effecting requests.

## Supported render operations

- MLT producers/playlists, multitrack composition, gaps, hard cuts, cross dissolve, spatial luma wipe and slide transitions. At most two clips overlap on each of eight video tracks; overlaps require an explicit matching transition.
- FFmpeg prepares frame-trimmed, scaled, normalized H.264 intermediates. Originals remain unchanged. MLT performs sequencing, compositing, audio mixing and H.264/AAC MP4 encoding.
- Brightness (-1..1), contrast (0..4), saturation (0..3), Gaussian blur (sigma 0..20), shadow color correction (red/green/blue -0.5..0.5), fade-in/fade-out (integer clip frames), and built-in warm/cool LUTs.
- Digital zoom (1..4), pan/tilt (-1..1), with optional ordered, clip-relative value keyframes. Camera interpolation is linear. No user filesystem paths or arbitrary LUT/filter/command strings are accepted.
- Source-audio gain (0..4), volume keyframes, transition audio fades, and up to 16 explicit music/audio clips with independent gain and fades. Output is stereo 48 kHz AAC.
- Titles/subtitles use frame-positioned text overlays, including text containing punctuation. Pillow renders private RGBA images; FFmpeg overlays them after MLT composition. This avoids relying on optional FFmpeg drawtext support. Built-in font glyph coverage is limited; this is not a full typography or subtitle-file import system.
- Output presets: landscape 1920x1080, portrait 1080x1920, square 1080x1080; previews preserve aspect at 640x360, 360x640 or 640x640. Output rates: 24, 25, 30, 50, 60, 24000/1001, 30000/1001 or 60000/1001. `output.fit` selects contain or cover.
- QC verifies nonempty/probeable output, dimensions, rational frame rate, expected duration, audio presence, and full decode when enabled. A job completes only after QC and committed export metadata.

`GET /api/v1/effects`, `/transitions`, `/render-presets` and `/audio/capabilities` describe the contract. `GET /api/v1/projects/{project_id}/edits/{version_id}/timeline` includes deterministic compiled operations. Tracking, subject masks, speed ramps, stabilization, advanced color matching and beat detection are not implemented or advertised.

## R2 storage and resumable uploads

The environment templates select `STORAGE_BACKEND=r2` as requested. Set `R2_ENDPOINT_URL=https://ACCOUNT_ID.r2.cloudflarestorage.com`, `R2_BUCKET`, `R2_ACCESS_KEY_ID` and `R2_SECRET_ACCESS_KEY`. R2 uses boto3's S3-compatible multipart transfers with bounded concurrency. See [Cloudflare's boto3 contract](https://developers.cloudflare.com/r2/examples/aws/boto3/). No R2 bucket or paid resources are provisioned by this backend. Missing R2 settings fail closed with `storage_unconfigured`; no credentials are committed. Set `STORAGE_BACKEND=local` for filesystem-only operation.

`MEDIA_STORAGE_ROOT` is a private render workspace and cache when R2 is selected. Source uploads, derived thumbnails/proxies and successful exports are published to R2. A worker materializes missing objects atomically before processing; authorized download endpoints stream from private staging with byte-range support. Local disk must have capacity for in-flight videos and intermediates. Cache files remain available for reuse; there is no automatic eviction of active media.

For large files:

1. `POST /api/v1/projects/{project_id}/assets/upload-sessions` with `{"filename":"clip.mp4","expected_size":12345}`.
2. `PATCH .../upload-sessions/{session_id}/chunks` with raw bytes and `Upload-Offset: 0`, then the returned offset on each following chunk. Each request is bounded by `UPLOAD_CHUNK_SIZE_BYTES`.
3. `GET .../upload-sessions/{session_id}` retrieves the committed offset for resume.
4. `POST .../upload-sessions/{session_id}/finalize` probes and publishes the completed upload. Repeated finalization returns the same asset.

Session offsets are serialized with row locks, flushed/fsynced before commit, and validated against expected size. Uncommitted extra bytes are truncated on resume. Sessions expire after `UPLOAD_SESSION_TTL_SECONDS`; cleanup records their file deletion. Open-session, upload-size, storage, project, concurrent-render and monthly-render limits are configurable.

## Migrations, tests, and checks

```bash
cd server
uv run alembic upgrade head
uv run pytest -q
uv run pytest -q -m media
AUTOCUT_RUN_INTEGRATION=1 STORAGE_BACKEND=local uv run pytest -q -m integration
uv run ruff check app alembic tests
uv run mypy app
```

Media tests generate synthetic clips and execute FFmpeg and MLT. Integration tests are opt-in with `AUTOCUT_RUN_INTEGRATION=1`; they use the configured PostgreSQL/Redis services, create a randomly named temporary PostgreSQL schema, apply all real migrations there, and remove only that schema afterward. They never migrate or clear the public schema. The real-worker test starts a temporary Celery process with its own namespaced Redis queue and stops it afterward. Set a dedicated test database URL via `DATABASE_URL` when preferred. Tests requiring a missing executable or explicit service opt-in report a skip, not a pass. Backups and restore tests belong to operations: restore PostgreSQL together with the corresponding immutable media files and storage root, since database rows reference those files by key.

## Storage and consistency notes

Originals are staged under UUID keys using streaming writes and atomic rename, then published through local or R2 storage. Derived thumbnails, proxies, and render files are stored under separate keys. APIs resolve files through the storage abstraction and check project ownership before streaming; single byte-range downloads are supported. Database soft deletion and active-job checks protect media referenced by edit versions. A cleanup/retention policy must retain any source used by a saved version or output.

Redis cache entries are namespaced and tenant-scoped where appropriate, expire with jitter, and may be missed without changing database correctness. Cache invalidation follows committed project writes. Redis locks are leases with random ownership tokens; PostgreSQL state and fencing remain authoritative. The initial data model uses indexed PostgreSQL tables and stable bounded pagination; it does not assume sharding or replica routing.


## Worker reliability and recovery

Jobs, ordered job events and dispatch-outbox entries commit together. Dispatch uses `FOR UPDATE SKIP LOCKED`, explicit queues, bounded broker timeouts and exponential retry with jitter. At-least-once deliveries are expected: only pending/queued jobs can be claimed, and each claim increments a PostgreSQL fencing token. Workers use a persistent event loop per process for asyncpg and Redis pools. TLS Redis verifies certificates.

Each attempt writes unique intermediate/export keys, so stale attempts cannot replace or delete a newer result. Leases heartbeat during media operations; cancellation terminates the media process group, and the watchdog stops media children if their worker disappears. Recovery fences stale attempts and requeues them up to `MAX_JOB_RETRIES`. Transient network/transaction failures retry; invalid media/plans and unsupported operations fail with durable codes. Failed jobs remain inspectable and have a bounded manual retry endpoint.

File cleanup intents are committed before publication and removed in the transaction that establishes the durable reference. Asset/export deletion commits a cleanup intent with the database change, avoiding a database/object-store dual write. The periodic cleaner retries failed deletions, expires abandoned upload sessions and removes unreferenced reserved keys. Soft-deleted projects retain their source media and immutable history; automatic permanent project purging is deliberately disabled. Assets referenced by saved versions cannot be deleted.

Lock order is user, project, upload session when applicable; worker completion locks job then asset. PostgreSQL row locks, uniqueness constraints and lifecycle/immutability triggers provide correctness. Redis lease locks use owner tokens and TTLs for optional coordination, and never replace database fencing. Redis caching is cache-aside with tenant scopes, TTL jitter, bounded single-flight locks, negative caching only when explicitly enabled, and graceful degradation. Project caches invalidate after commits; usage summaries may lag by up to 30 seconds and are never used for quota decisions. No write-back cache is used.

All four Alembic revisions are under `alembic/versions/`: frozen initial PostgreSQL DDL, edit-version immutability, durable file deletions, and job lifecycle invariants. Normal startup does not create tables. API OpenAPI and range downloads are authenticated where applicable; registries and health are public. Metrics are process-local Prometheus counters/histograms unless an operator configures Prometheus multiprocess collection.

## Current local verification

A verification report is maintained in `VERIFICATION.md`. R2 live round trips require credentials; isolated SDK-adapter tests do not substitute for a live bucket test. No Docker, frontend, AI service or infrastructure provisioning is involved.
