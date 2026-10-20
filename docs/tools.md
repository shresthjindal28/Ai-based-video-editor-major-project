# AutoCut AI — TOOLS.md

## Purpose

This document defines the selected technology stack for **AutoCut AI**, a fully autonomous, professional-grade video editing platform. Users upload raw clips, describe the edit, and receive a rendered video with cinematic cuts, compositing, color grading, sound design, and revisions.

**Cost policy:** All selected software must be free to download and self-host, with no mandatory paid API or subscription. Free software does **not** mean free GPU hardware, electricity, storage, bandwidth, hosting, or copyrighted media. Review licenses and codec/patent requirements before commercial distribution.

## 1. Fixed application stack

| Layer | Selected tools | Role |
|---|---|---|
| Frontend | **Next.js App Router, React, strictly TypeScript, Tailwind CSS v4** | Web application; no JavaScript source files for app logic |
| UI components | **shadcn/ui, Radix UI, Lucide** | Accessible controls and interface |
| Frontend data/state | **TanStack Query, Zustand, Zod** | API caching, workflow state, validation |
| Authentication | **Better Auth** (self-hosted in Next.js) | Sessions, login, account management |
| Main backend | **Python 3, FastAPI, Pydantic v2, Uvicorn** | Projects, assets, edit jobs, rendering orchestration, exports |
| AI backend | **Python 3, FastAPI, Pydantic v2** | Video understanding, editing decisions, structured edit plans |
| Python tooling | **uv, Ruff, pytest, mypy** | Dependency management, formatting, testing, typing |
| Database | **PostgreSQL, SQLAlchemy 2, Alembic, asyncpg** | Durable app data and migrations |
| Optional semantic search | **pgvector** | Search among scene and shot embeddings |
| Cache / job broker | **Redis + Celery** | Background jobs, retries, cancellation coordination |
| Media storage | **Local filesystem in development; self-hosted S3-compatible storage in production** | Originals, proxies, previews, exports |
| Infrastructure | **Docker Engine / Compose on supported environments** | Reproducible local and self-hosted services |
| Observability | **Prometheus, Grafana, OpenTelemetry** | Logs/metrics/traces and render monitoring |

**Better Auth integration:** Better Auth runs in the TypeScript/Next.js service, not as a Python library. Python APIs must validate the authenticated session or a securely issued internal credential, enforce project ownership, and never trust a client-provided user ID. Choose and implement one verified cross-service auth contract before exposing protected endpoints.

## 2. AI models — no paid inference API

| Capability | Free/self-hosted choice | Notes |
|---|---|---|
| Primary editing planner | **DeepSeek-R1-Distill-Qwen-7B** | Start with quantized local inference; upgrade to 14B/32B when hardware permits |
| Local model runtime | **Ollama** | Simple local development |
| Higher-throughput serving | **vLLM** | Optional production GPU inference, subject to model/runtime compatibility |
| Frame / shot understanding | **Qwen2.5-VL** | Separate vision-language model; DeepSeek text model cannot see footage by itself |
| Transcription | **faster-whisper** with compatible Whisper weights | Spoken dialogue and timestamps |
| Scene detection | **PySceneDetect** | Candidate cuts and shot boundaries |
| Visual similarity | **OpenCLIP** | Semantic matching and candidate match cuts |
| Segmentation / masks | **SAM 2** | Advanced subject isolation; optional GPU-heavy feature |
| Object tracking | **OpenCV tracking + optical flow** | Movement, reframing, and tracking |
| Audio analysis | **librosa, SciPy, NumPy** | Beats, silence, onsets, loudness features |

**DeepSeek policy:** Use locally hosted DeepSeek open weights, **not** the paid DeepSeek API. The selected DeepSeek-R1-Distill-Qwen variants are released under MIT terms, with underlying Qwen attribution/license obligations. Full DeepSeek-R1 is far too large for typical personal hardware. Check each additional model's current license before commercial use.

**AI output contract:** The AI produces a **versioned, validated JSON edit decision list (EDL)**, never raw shell commands or arbitrary executable code. All clip IDs, source ranges, effect names and parameters are checked by the main backend.

## 3. Professional-grade editing and rendering engine

This is the most important technical choice. **Do not use MoviePy or Remotion as the primary professional rendering engine.** They can be useful for narrow tasks, but the core must support frame-accurate multitrack compositions, audio, transitions, and advanced effects.

| Tool | Role | Priority |
|---|---|---|
| **MLT Multimedia Framework** | Primary non-linear, multitrack editing/compositing engine; timeline, transitions, filters, keyframes | **Core** |
| **FFmpeg + ffprobe** | Ingestion, codec inspection, proxies, transcoding, filtering, muxing and final export | **Core** |
| **frei0r plugins** | Additional video filters and creative effects supported by the host engine | **Core** |
| **OpenColorIO** | Managed color transforms and consistent color pipeline | **Advanced** |
| **OpenImageIO** | High-quality image/sequence operations and metadata | **Advanced** |
| **OpenCV** | Optical flow, stabilization, masks, computer vision preprocessing | **Advanced** |
| **libvidstab / FFmpeg vidstab** | Video stabilization | **Advanced** |
| **OpenTimelineIO** | Editorial timeline interchange where compatible | **Later** |
| **Blender (headless)** | Advanced 3D titles, camera moves, compositing and VFX shots | **Optional advanced** |
| **Rubber Band Library** | High-quality audio time-stretch / pitch operations | **Optional advanced** |
| **FFmpeg audio filters** | Mixing, crossfades, normalization, EQ, compression, ducking | **Core** |

**Why MLT + FFmpeg:** MLT is an actual nonlinear video editing framework used in professional-capable editors such as Kdenlive; FFmpeg is an industry-standard media processing toolkit. Together they are a more serious foundation for this product than simple concatenation scripts.

**Rendering architecture:**
1. Inspect and normalize input media; preserve originals.
2. Create low-resolution proxy assets and reusable analysis data.
3. Generate a canonical timeline JSON with exact frame/time positions, tracks, clips, transitions, keyframes, effects and audio routing.
4. Validate the timeline, dependencies, codecs and effect compatibility.
5. Compile timeline operations into MLT compositions and FFmpeg processing steps; use specialized OpenCV/Blender processing when required.
6. Render low-resolution previews before expensive full-resolution exports.
7. Run automated output quality checks and save reproducible version metadata.

**Supported editing families (implementation targets):**
- Hard, jump, match, J/L, smash and cutaway edits; montage and beat-synchronized sequencing.
- Multitrack overlays, masks, fades, dissolves, wipes, zooms, slides and whip-pan transitions.
- Keyframed pan/tilt/zoom, speed ramps, stabilization, motion blur, tracking and reframing.
- White balance, exposure, contrast, highlights/shadows, color matching, LUTs, creative grading and film grain.
- Gaussian/directional/radial blur, subject isolation, background fill, chroma key and compositing.
- Audio cleanup, dialogue mixing, crossfades, music ducking, beat detection and captions.
- Portrait/landscape/square exports, configurable resolution, codec and bitrate.

Some effects require custom processing and careful GPU/CPU benchmarking; listing them here does **not** mean they are natively available as one MLT filter.

## 4. Service boundaries

### `frontend/` (or existing Next.js application folder)
- Next.js App Router with **TypeScript strict mode enabled**; Tailwind CSS only for app styling.
- Upload manager, AI creative brief, job progress, video preview, conversational revisions, export/download screens.
- Better Auth session management.

### `server/` or `backend/` — Main Python backend
- Module-wise FastAPI: `auth` integration, `users`, `projects`, `assets`, `uploads`, `editor`, `timelines`, `effects`, `jobs`, `rendering`, `exports`, `storage`.
- Owns PostgreSQL application records, permissions, edit versions and rendering jobs.
- Owns the deterministic editing compiler and render workers.

### `ai-backend/` — Separate Python AI backend
- Module-wise FastAPI: `llm`, `vision`, `scene_detection`, `transcription`, `audio_analysis`, `motion_analysis`, `color_analysis`, `shot_selection`, `editing_planner`, `timeline_generation`, `video_quality`.
- Analyzes assets and returns validated creative/editing plans.
- Does not own user authentication, final exports, or directly execute arbitrary user-supplied commands.

## 5. Storage and background processing

- **PostgreSQL:** users/projects, media metadata, edit requests, versions, timeline documents, job states, export records, permissions.
- **Redis + Celery:** queued analysis, inference, preview and render jobs with retries and worker concurrency limits.
- **Filesystem initially:** media originals, proxies, frame samples, masks, temporary renders and exports.
- **Self-hosted object storage later:** large uploads, immutable source media and downloadable output objects. Select a currently open-source, commercially usable S3-compatible implementation after reviewing its license.
- **Presigned or resumable uploads:** large media must not be buffered in FastAPI memory.

## 6. Testing and quality gates

- **pytest + pytest-asyncio + httpx:** API and service tests.
- **Ruff + mypy:** Python formatting/linting/static checks.
- **TypeScript `strict: true` + ESLint + Prettier:** frontend quality.
- **Vitest + Playwright:** UI and end-to-end browser tests.
- **Golden render tests:** compare short reference clips for expected cuts, frame boundaries, audio sync, effects and output format.
- **ffprobe QC:** verify output duration, streams, fps, resolution, codecs and timestamps.
- **Prometheus/Grafana/OpenTelemetry:** measure render time, GPU/CPU use, failures, queue wait and inference latency.

## 7. Non-negotiable rules

1. **Free and self-hostable software only.** No mandatory subscription, paid AI API, paid editing SDK or paid hosted service.
2. **No promise of zero infrastructure cost.** GPU rendering, storage and bandwidth consume real resources.
3. **Strict TypeScript** in the Next.js app. Python for both backend services.
4. **PostgreSQL** is the primary database. **Better Auth** owns web authentication.
5. **DeepSeek** is the primary text editing planner; dedicated vision/audio models handle other modalities.
6. **MLT + FFmpeg** form the professional editing core, with extensible specialized processors.
7. **No destructive editing.** Preserve source footage and version each edit.
8. **No hallucinated timestamps.** Every referenced shot must exist in analyzed footage.
9. **No raw LLM-generated shell execution.** Compile only validated editing operations.
10. **Keep features module-wise** in both Python services.
11. **Licenses matter:** MLT, FFmpeg, frei0r, Blender, codecs and model weights may have LGPL/GPL, patent, or attribution obligations depending on builds and distribution. Validate before shipping a commercial product.
12. **Prioritize quality:** reliable playback, frame accuracy, color consistency and audio synchronization before adding novelty effects.

## 8. Build order

1. Upload, probe, proxy, project metadata and object storage abstraction.
2. FFmpeg + MLT rendering proof of concept: multi-clip timeline, audio track, transitions, grade, zoom and export.
3. Canonical edit JSON schema and deterministic timeline compiler.
4. Local DeepSeek prompt-to-edit-plan integration with strict validation.
5. Scene detection, speech, audio and vision analysis.
6. Autonomous shot selection, pacing, beat sync and color decisions.
7. Conversational revisions, previews, version history and retries.
8. Advanced tracking, masks, compositing, color management, 4K pipeline and scaling.

## References

- MLT: https://mltframework.org/ and https://github.com/mltframework/mlt
- FFmpeg: https://ffmpeg.org/documentation.html
- Kdenlive (MLT-based editor reference): https://github.com/KDE/kdenlive
- DeepSeek-R1 model and license: https://huggingface.co/deepseek-ai/DeepSeek-R1
- Better Auth: https://github.com/better-auth/better-auth

**Status:** Architecture/tool selection document. Tools are selected, not claimed installed or implemented.
