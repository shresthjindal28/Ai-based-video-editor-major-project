# AutoCut AI — Main Problem Understanding

## 1. What We Are Actually Building

AutoCut AI is a **fully autonomous, AI-directed video editing SaaS platform**. A user uploads raw clips, optionally supplies music or reference material, and describes the desired final video in everyday language. The platform understands the media, plans the edit, executes supported operations, renders a preview, and delivers an export. The user can request changes conversationally.

**This is not** a text-to-video generator, a chatbot that only recommends edits, a caption generator, or a conventional manual timeline editor with an AI button. It is an end-to-end editing system that performs the work on existing footage.

## 2. Canonical User Journey

1. **Create a project:** Choose a title or start directly with uploads.
2. **Upload source media:** Multiple clips; optionally music, voiceover, logos, and style references.
3. **Ingest and inspect:** Verify files, extract metadata, make thumbnails/proxies, and store originals unchanged.
4. **Describe the edit:** Example: “Make a 60-second warm cinematic reel, start with the drone shot, cut on beats, use gentle tilt and zoom, and fade to black.”
5. **Analyze content:** Detect scenes, transcribe speech, classify shots, estimate motion/sharpness, and inspect music beats.
6. **Plan:** Produce a constrained shot list, exact source ranges, timing, effects, transitions, audio plan, and output profile.
7. **Validate:** Ensure every referenced asset, timestamp, effect, and parameter is legal and supported.
8. **Render preview:** Execute the plan using media-processing workers; show stage-by-stage progress.
9. **Review:** User watches the preview and can ask for targeted changes.
10. **Revise:** Create a new immutable edit version, ideally reusing unaffected analysis and render intermediates.
11. **Export:** Render and validate the requested final resolution/format; provide secure download.

## 3. Functional Requirements

### 3.1 Media Management

- Upload many video clips with progress, retry, and resumability.
- Accept a documented subset of codecs and containers initially.
- Probe duration, dimensions, frame rate, rotation, codec, color metadata, and audio tracks.
- Preserve originals; create low-resolution proxies, thumbnails, waveforms, and extracted frame samples.
- Keep assets associated with their owning project and user.

### 3.2 Natural-Language Editing

- Understand intent such as “fast-paced,” “cinematic,” “vintage,” “subtle,” “emotional,” or “energetic.”
- Resolve concrete constraints: target duration, aspect ratio, source order, mandatory shots, excluded clips, music, and output format.
- Ask for clarification only when an essential creative or technical requirement is contradictory or missing.
- Convert prompts to a structured, auditable edit specification rather than directly executing generated shell commands.
- Support revision instructions such as “remove clip 3,” “make the first 10 seconds faster,” or “use less saturation.”

### 3.3 Video Understanding

- Scene and shot boundary detection.
- Timestamped descriptions of visible content, actions, and locations when visually grounded.
- Speech transcription and optional word-level timing.
- Motion, blur/sharpness, exposure, and duplicate/near-duplicate scoring.
- Optional object/person detection and tracking for advanced features.
- Semantic retrieval of moments relevant to a user's prompt.

### 3.4 Editing Capabilities

| Category | Operations | Priority |
|---|---|---|
| Assembly | Order, trim, split, concatenate, remove pauses | MVP |
| Cuts | Hard cuts, jump cuts, fade to black, cross dissolve | MVP |
| Advanced cuts | J-cuts, L-cuts, match cuts, smash cuts, cross-cutting | Later |
| Transitions | Wipes, slides, zooms, whip pans, masked transitions | Basic MVP; advanced later |
| Color correction | Exposure, white balance, contrast, saturation, highlights/shadows | MVP |
| Color grading | Warm/cool styles, LUTs, cinematic looks, shot matching | Basic MVP; advanced later |
| Motion | Digital pan, tilt, zoom, rotation, keyframes | MVP |
| Motion advanced | Speed ramps, subject tracking, parallax, motion blur | Later |
| Blur and compositing | Gaussian blur, background fill, overlays | MVP |
| Compositing advanced | Segmentation masks, selective blur, chroma key, tracking | Later |
| Audio | Mixing, fades, gain, normalization, music placement | MVP |
| Audio advanced | Beat sync, dialogue ducking, sound effects, denoising | Later |
| Text | Titles, simple subtitles, watermarks | MVP |
| Text advanced | Kinetic typography, tracked text, motion graphics | Later |
| Export | Vertical, horizontal, square, configurable encoding | MVP |

A requested effect must either be executed by a supported backend implementation or reported as unsupported. The model must not claim to have applied an effect that was not rendered.

## 4. The Hardest Conceptual Problem

A prompt like **“make it cinematic” is underspecified**. The platform must translate subjective intent into explicit choices while respecting the actual footage:

- Which shots best communicate the story?
- Which segments are visually usable?
- What is the intended pace and emotional arc?
- How long should each shot remain on screen?
- Should audio bridge between clips (J/L cuts)?
- Which transitions are appropriate, rather than simply flashy?
- What color treatments are compatible across different lighting conditions?
- How can the system preserve important subjects when converting 16:9 footage to 9:16?

The system should use **interpretable editing policies, visual/audio evidence, explicit user constraints, and validated tool operations**, not assume that a language model alone can make perfect artistic judgments.

## 5. Separation of Responsibilities

### AI Planning Layer

Interprets prompts, chooses shots, creates narrative structure, selects supported effects, and explains decisions. It operates on timestamped metadata, sampled frames, transcripts, and audio features.

### Deterministic Editing Layer

Owns the canonical timeline, effect registry, timing calculations, transition overlap, audio routing, frame transformations, and render compilation. It validates all model output.

### Media Processing Layer

Executes FFmpeg filter graphs and specialized processing routines; performs encoding, compositing, normalization, stabilization, and exports.

### Workflow Layer

Coordinates long-running ingestion, analysis, planning, preview, QC, and final export. It provides retries, cancellation, idempotency, progress events, and checkpoints.

### User Experience Layer

Offers project creation, upload, prompt entry, rendering status, preview, natural-language revisions, version comparison, and downloads. A manual editing timeline is not required for the MVP.

## 6. Representative Example

**Input assets:** Eight short travel clips and one licensed music track.

**User prompt:**

> Combine the best beach and sunset clips into a 45-second vertical reel. Remove shaky or boring sections, add warm cinematic grading, use gentle tilt and zoom, sync important cuts to the beat, apply smooth transitions, and end with a fade to black.

**Expected processing:**

1. Inspect source clips and music.
2. Detect candidate shots and identify beach/sunset content.
3. Rank candidates by relevance, visual quality, and diversity.
4. Construct a 45-second shot sequence using source-valid timestamps.
5. Place cuts near useful beat markers where appropriate.
6. Add supported zoom/tilt keyframes, grading and transitions.
7. Compile and render a 9:16 preview.
8. Check playback, black frames, audio peaks, dimensions, and timing.
9. Show the preview and accept revisions.

**Expected output:** A downloadable video plus a saved, versioned edit specification. It should not claim a specific creative quality score without evaluation.

## 7. Recommended Technology Boundaries

| Subsystem | Initial Choice | Reason |
|---|---|---|
| Web application | Next.js, TypeScript, Tailwind, shadcn/ui | Familiar full-stack frontend |
| API | FastAPI, Pydantic | Typed endpoints and validation |
| Database | PostgreSQL, SQLAlchemy, Alembic | Durable metadata and versioning |
| Storage | S3-compatible object storage | Large media outside database |
| Background jobs | Redis + Celery initially | Asynchronous processing |
| LLM planning | Qwen-family instruct model via Ollama (development) | Local, structured planning |
| Visual understanding | Qwen vision-language model | Scene/frame descriptions |
| Transcription | faster-whisper | Speech understanding |
| Scene detection | PySceneDetect | Candidate shot segmentation |
| Beat analysis | librosa | Music-aware cuts |
| Video rendering | FFmpeg | Reliable filter graphs and encoding |
| Optional tracking | OpenCV / segmentation model | Advanced masking/reframing |
| Observability | OpenTelemetry + logs/metrics | Debug long-running workflows |

Model names and sizes are provisional. Benchmark quality, throughput, hardware needs, and commercial licensing before committing to a production deployment.

## 8. Data Model Understanding

**Main entities:** `User`, `Project`, `MediaAsset`, `AssetAnalysis`, `Scene`, `EditRequest`, `EditVersion`, `TimelineItem`, `EditJob`, `JobEvent`, `RenderOutput`, `UsageRecord`.

- A user owns projects.
- A project contains media assets and many edit requests/versions.
- An asset can have reusable analyses and scenes.
- An edit version contains an immutable structured timeline referencing source assets.
- A job executes a particular stage/version and records status/events.
- A render output points to a versioned artifact in object storage.

Avoid storing raw video bytes in PostgreSQL. Enforce authorization on every project, asset, job, and output.

## 9. Canonical Edit Plan Contract

The platform needs a strict, versioned schema containing:

- Project, request, and schema identifiers.
- Output resolution, aspect ratio, frame rate, and codec profile.
- Source asset IDs and bounded source in/out positions.
- Timeline positions and durations using frame/rational time semantics.
- Tracks for video, audio, overlays, and captions.
- Ordered effect stacks with whitelisted effect names and validated parameters.
- Transition types, durations, and overlap semantics.
- Audio mixing, gain, fades, and synchronization instructions.
- Provenance linking edit decisions to user requests and analysis evidence.

**Never execute arbitrary FFmpeg command strings produced directly by the LLM.** Compile only supported operations from validated structured data.

## 10. Non-Functional Requirements

- **Reliability:** Durable jobs, retries, cancellation, resumable uploads, and idempotent stages.
- **Performance:** Proxy-based previews, caching, batched inference, and reusable analysis.
- **Scalability:** Separate CPU workers, GPU inference workers, and rendering workers as load grows.
- **Security:** Signed URLs, tenant isolation, strict media validation, isolated processing, bounded resources, and safe file handling.
- **Privacy:** Configurable retention, deletion, access logging, and no unapproved reuse of private uploads for training.
- **Cost control:** Limits on upload size, video duration, output resolution, concurrency, and GPU usage.
- **Observability:** Stage durations, error types, inference latency, rendering time, and cost per completed minute.
- **Reproducibility:** Versioned plans, model/prompt versions, effect versions, and immutable originals.
- **Compatibility:** Correct handling of variable-frame-rate inputs, mixed codecs, rotation metadata, and audio synchronization.

## 11. Primary Engineering Risks

1. **Subjective quality:** Automated edit decisions can be technically correct but creatively weak.
2. **LLM hallucination:** A model may reference nonexistent scenes, unsupported effects, or invalid time ranges.
3. **Timeline correctness:** Transitions, speed changes, and audio overlaps can create drift or discontinuities.
4. **Rendering cost:** Multiple large clips and high-resolution effects are expensive.
5. **Heterogeneous media:** Frame rates, color spaces, orientation, and codecs differ between uploads.
6. **Model licensing:** Some open-weight models and libraries require careful commercial-use review.
7. **Failure recovery:** Jobs must resume safely after worker restarts without duplicate billing or corrupted outputs.

## 12. MVP Acceptance Scenarios

- **Assembly:** Given three valid clips, the platform creates a playable combined video in the requested order.
- **Prompt-based trimming:** Given a request to remove the first two seconds of a clip, the resulting plan and output reflect the change within frame tolerance.
- **Effects:** Given a supported warm grade and zoom request, the render contains those operations, and the plan records their parameters.
- **Invalid instruction:** If the prompt requests a nonexistent clip or unsupported effect, the platform explains the limitation instead of pretending it succeeded.
- **Revision:** A follow-up instruction creates a new edit version without altering the previous output or original media.
- **Export:** The exported file meets the selected dimensions, frame rate, codec, and duration tolerance.
- **Resilience:** A worker crash can be retried without losing the project or duplicating final artifacts.
- **Security:** One user cannot retrieve another user's source files, jobs, or exports.

## 13. Development Phases

### Phase 1 — Deterministic Editing Foundation

Build uploads, metadata extraction, storage, a typed edit-plan schema, FFmpeg compilation, simple transitions/effects, preview rendering, and export. Use handcrafted plans to verify correctness before introducing an LLM.

### Phase 2 — Natural-Language Editing

Connect an open-weight LLM to produce schema-constrained edit plans; add validation, repair, prompt history, and conversational revisions.

### Phase 3 — Multimodal Media Understanding

Add scene detection, transcripts, frame descriptions, semantic retrieval, and quality scoring to ground edit decisions in actual footage.

### Phase 4 — Autonomous First Cuts

Implement shot selection, sequencing, pacing, color/style policies, and automatic first-draft rendering from user intent.

### Phase 5 — Advanced Creative Editing

Introduce beat synchronization, subject tracking, advanced cuts, masking, stabilization, speed ramps, and richer audio treatment.

### Phase 6 — Production SaaS

Add authentication, billing/quotas, retention controls, robust workflow orchestration, metrics, scalable worker pools, and security hardening.

## 14. What Success Looks Like

The defining experience is:

**Upload raw clips → Describe the intended result → Receive a complete first cut → Request changes in plain language → Export.**

The user should never be required to manually operate a timeline for a supported task. The system must remain transparent about what it did, what it could not do, and why.

## 15. Open Product Decisions

Before implementation, finalize:

- Primary customer segment: reels creators, marketers, vloggers, or professional editors.
- Initial maximum upload size, number of clips, and total source duration.
- Supported input codecs and maximum output resolution.
- First release's exact effect whitelist.
- Whether music is user-provided only or selected from a licensed library.
- Local-only development versus managed GPU inference in production.
- Free tier limits, storage retention, and rendering quotas.
- Objective and human-evaluated quality benchmarks for automated edits.

These are product decisions, not reasons to delay the first deterministic editing prototype.
