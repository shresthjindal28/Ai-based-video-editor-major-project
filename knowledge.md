# AutoCut AI — Project Knowledge

## Product
AutoCut AI is an autonomous video editing SaaS that turns existing raw footage and natural-language instructions into a complete, editable, reproducible video.

**User flow:** Upload clips → describe the desired edit → analyze media → generate and validate an edit plan → render preview → request conversational revisions → export.

Primary users are creators, marketers, casual users, and editors seeking automated first cuts. Supported tasks must work without requiring a manual timeline. Generating new footage from text is outside the initial scope.

## Architecture and Selected Stack
- **Frontend:** Next.js App Router, React, strict TypeScript, Tailwind CSS v4, shadcn/ui, Radix UI, Lucide; TanStack Query, Zustand, and Zod.
- **Authentication:** Self-hosted Better Auth in Next.js. Python APIs must verify a defined cross-service authentication contract and enforce ownership.
- **Main backend:** Modular Python FastAPI/Pydantic v2 service owning projects, assets, permissions, timelines, jobs, deterministic compilation, rendering, and exports.
- **AI backend:** Separate modular Python FastAPI service for media analysis, shot selection, and structured editing plans.
- **Data and jobs:** PostgreSQL, SQLAlchemy 2, Alembic, asyncpg; Redis + Celery. Store media on the local filesystem initially, with a self-hosted S3-compatible storage abstraction for production.
- **AI:** Local DeepSeek-R1-Distill-Qwen-7B via Ollama for text planning; Qwen2.5-VL for vision, faster-whisper for transcription, PySceneDetect for scenes, and librosa/SciPy/NumPy for audio. OpenCLIP, SAM 2, and OpenCV support advanced analysis.
- **Rendering:** MLT is the primary multitrack editing/compositing engine; FFmpeg/ffprobe handle media inspection, proxies, processing, encoding, and QC. Use frei0r and specialized processors as needed. MoviePy and Remotion are not the primary engine.

The concrete selections in `tools.md` refine the earlier provisional recommendations: use DeepSeek for text planning and MLT + FFmpeg for the editing core.

## Editing Contract and Data
AI directs editing; deterministic software renders it. AI returns a strict, versioned JSON edit decision list containing source IDs/ranges, frame-accurate timing, tracks, effects, transitions, keyframes, audio routing, output settings, and provenance. Validate assets, timestamps, parameters, overlaps, and supported operations before compilation. Never execute raw model-generated shell commands.

Core entities: User, Project, MediaAsset, AssetAnalysis, Scene, EditRequest, EditVersion, TimelineItem, EditJob, JobEvent, RenderOutput, and UsageRecord. Preserve originals and immutable edit versions; reuse analysis and intermediates where possible. Store media outside PostgreSQL.

## Initial Scope and Build Order
1. Build uploads, probing, proxies, thumbnails, project metadata, and storage abstraction.
2. Prove deterministic MLT + FFmpeg rendering and establish the canonical timeline schema/compiler using handcrafted plans.
3. Add validated local DeepSeek prompt-to-plan generation.
4. Ground decisions in scene, speech, audio, and visual analysis.
5. Add autonomous selection/pacing, conversational revisions, previews, version history, and reliable retries.
6. Expand into advanced tracking, masks, beat sync, stabilization, speed ramps, compositing, and scaling.

MVP editing covers selection, trimming, ordering, basic transitions, color/LUT adjustments, pan/tilt/zoom, blur, simple audio mixing, optional titles/subtitles, and vertical/horizontal/square exports. Advanced features are targets, not claims of current support; the exact initial effect whitelist remains to be finalized.

## Non-Negotiables and Validation
- Free, self-hostable software; no mandatory paid APIs, subscriptions, or editing SDKs. Infrastructure still costs money; review software/model licenses and codec obligations before shipping.
- Ground every shot and timestamp in actual footage. Explain unsupported requests and never claim an unrendered effect succeeded.
- Preserve media, isolate tenants and processing, use secure downloads, and bound upload/render resources.
- Run long jobs asynchronously with progress, retries, cancellation, idempotency, and durable state.
- Prioritize playable output, frame accuracy, color consistency, and audio sync. Verify exports with ffprobe and meaningful render/API/UI tests; use Ruff/mypy and strict TypeScript checks.

Proposed acceptance targets include ≥90% schema-valid supported plans, ≥95% accepted MVP jobs yielding a playable preview or actionable failure, and all completed exports passing technical QC. These targets are unmeasured.

## Open Decisions and Status
Finalize the primary customer segment, upload/duration limits, supported codecs, output resolution, effect whitelist, music sourcing, production inference hardware, quotas/retention, and quality benchmarks.

These documents define requirements and selected architecture; they do not establish that tools are installed or features implemented.

**Sources:** `PROBLEM_STATEMENT.md`, `PROBLEM_UNDERSTANDING.md`, and `tools.md`.
