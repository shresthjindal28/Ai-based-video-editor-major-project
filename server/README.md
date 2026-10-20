# AutoCut main backend

This directory contains the Python resource server for AutoCut AI. It owns users synchronized from Better Auth, projects, source media, immutable edit plans, render jobs, and exports. The AI worker and frontend remain separate services.

## Local requirements

- Python 3.12 or newer and `uv`
- PostgreSQL
- Redis
- FFmpeg and ffprobe
- MLT with the `melt` CLI and its `avformat` consumer, plus H.264/AAC codecs

The backend does not start containers or install system media packages. The API can start without PostgreSQL/Redis, but `/health/ready` returns 503 until both respond. Protected routes fail closed unless Better Auth JWT/JWKS settings are configured.

## Configure and run

Copy `.env.example` to `.env`, then fill in the database/auth settings for your local environment. `AUTH_ISSUER`, `AUTH_AUDIENCE`, and `AUTH_JWKS_URL` are intentionally blank in the checked-in files. The backend never accepts identity headers or an unverified user ID.

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
2. `POST /api/v1/projects/{project_id}/assets` streams one media file into private local storage, computes SHA-256, probes it with ffprobe, then queues thumbnail/proxy preparation. The asset is editable once its processing status is `ready`.
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

- H.264 MP4 output at the validated project presets; previews scale to 640 pixels on the long edge.
- Frame trimming, sequencing, hard cuts, gaps, and MLT luma transitions for cross dissolves and wipes.
- MLT brightness, contrast, saturation, static affine zoom/pan/tilt, and uniform box blur filters.
- Source audio and explicit audio tracks with gain and fade controls.
- ffprobe metadata checks, output dimensions/duration checks, and optional full decode checks with FFmpeg.

The edit contract is deliberately narrower than future product goals. Subject tracking, masks, stabilization, speed ramps, LUT color management, dynamic keyframes, and advanced audio automation are not advertised as implemented. MLT service availability and consumer codecs depend on the local MLT build.

## Migrations, tests, and checks

```bash
cd server
uv run alembic upgrade head
uv run pytest -q
uv run pytest -q -m media
uv run pytest -q -m integration
uv run ruff check app alembic tests
uv run mypy app
```

Media tests create synthetic clips with FFmpeg. PostgreSQL/Redis integration and actual MLT rendering require those local services and tools; pytest reports an explicit skip when they are absent. Do not use production data for test migrations. Backups and restore tests belong to operations: restore PostgreSQL together with the corresponding immutable media files and storage root, since database rows reference those files by key.

## Storage and consistency notes

Originals are written to a private local filesystem root using UUID keys and atomic rename. Derived thumbnails, proxies, and render files are stored under separate keys. APIs resolve files through the storage abstraction and check project ownership before streaming; single byte-range downloads are supported. Database soft deletion and active-job checks protect media referenced by edit versions. A cleanup/retention policy must retain any source used by a saved version or output.

Redis cache entries are namespaced and tenant-scoped where appropriate, expire with jitter, and may be missed without changing database correctness. Cache invalidation follows committed project writes. Redis locks are leases with random ownership tokens; PostgreSQL state and fencing remain authoritative. The initial data model uses indexed PostgreSQL tables and stable bounded pagination; it does not assume sharding or replica routing.
