from __future__ import annotations

import asyncio
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from uuid import UUID

from app.core.config import get_settings
from app.core.exceptions import ProcessError
from app.modules.editor.compiler import compile_plan
from app.modules.editor.schemas import TimelinePlan
from app.modules.rendering.media_probe import run_media_command
from app.modules.rendering.preprocessing import overlay_titles, prepare


def prop(element, name: str, value) -> None:
    ET.SubElement(element, "property", {"name": name}).text = str(value)


def build_mlt_xml(plan: TimelinePlan, assets: dict[UUID, Path], workdir: Path,
                  asset_rates: dict[UUID, tuple[int, int]] | None = None) -> Path:
    """Build MLT producers, track tractors, playlists, compositors and mixers.

    Rendering first applies FFmpeg normalization/effects. This XML builder owns
    sequencing, overlaps and compositing; no API-supplied XML is accepted.
    """
    compiled = compile_plan(plan)
    width, height = compiled.width, compiled.height
    end = max([c.timeline_start_frame+c.duration_frames for c in plan.clips] +
              [a.timeline_start_frame+a.duration_frames for a in plan.audio])
    root = ET.Element("mlt", {"LC_NUMERIC": "C", "version": "7.0.0", "producer": "main"})
    ET.SubElement(root, "profile", {"description": "AutoCut", "width": str(width), "height": str(height),
        "frame_rate_num": str(compiled.fps_num), "frame_rate_den": str(compiled.fps_den), "progressive": "1",
        "sample_aspect_num": "1", "sample_aspect_den": "1", "display_aspect_num": str(width),
        "display_aspect_den": str(height), "colorspace": "709"})
    background = ET.SubElement(root, "producer", {"id": "black"})
    prop(background, "mlt_service", "color")
    prop(background, "resource", "black")
    backdrop = ET.SubElement(root, "playlist", {"id": "background"})
    ET.SubElement(backdrop, "entry", {"producer": "black", "in": "0", "out": str(end-1)})
    clips = sorted(plan.clips, key=lambda c: (c.track, c.timeline_start_frame, str(c.id)))
    producer_ids = {}
    for index, clip in enumerate(clips):
        identity = f"clip_{index}"
        producer_ids[clip.id] = identity
        producer = ET.SubElement(root, "producer", {"id": identity})
        prop(producer, "mlt_service", "avformat")
        prop(producer, "resource", assets[clip.asset_id])
        prop(producer, "video_index", 0)
        prop(producer, "audio_index", 1)
        prop(producer, "threads", 2)
        prop(producer, "eof", "pause")
    audio_ids = []
    for index, audio in enumerate(plan.audio):
        identity = f"audio_{index}"
        producer = ET.SubElement(root, "producer", {"id": identity})
        prop(producer, "mlt_service", "avformat")
        prop(producer, "resource", assets[audio.asset_id])
        prop(producer, "video_index", -1)
        prop(producer, "audio_index", 0)
        playlist = ET.SubElement(root, "playlist", {"id": f"audio_playlist_{index}"})
        if audio.timeline_start_frame:
            ET.SubElement(playlist, "blank", {"length": str(audio.timeline_start_frame)})
        ET.SubElement(playlist, "entry", {"producer": identity, "in": str(audio.source_in_frame),
            "out": str(audio.source_in_frame+audio.duration_frames-1)})
        audio_ids.append(f"audio_playlist_{index}")
    # A generated PGM luma map gives wipe a real spatial threshold, rather
    # than advertising a dissolve under a second name.
    wipe_path = workdir / "wipe.pgm"
    wipe_path.write_bytes(b"P5\n64 64\n255\n" + bytes(round(x*255/63) for y in range(64) for x in range(64)))
    track_ids = []
    for track in sorted({c.track for c in clips}):
        lane_clips: dict[int, list] = {0: [], 1: []}
        ends = [0, 0]
        for clip in (c for c in clips if c.track == track):
            candidates = [lane for lane in (0, 1) if ends[lane] <= clip.timeline_start_frame]
            if not candidates:
                raise ProcessError("timeline_overlap", "Only two clips may overlap on a track", 422)
            lane = candidates[0]
            lane_clips[lane].append(clip)
            ends[lane] = clip.timeline_start_frame + clip.duration_frames
        for lane in (0, 1):
            playlist = ET.SubElement(root, "playlist", {"id": f"video_playlist_{track}_{lane}"})
            cursor = 0
            for clip in lane_clips[lane]:
                if clip.timeline_start_frame > cursor:
                    ET.SubElement(playlist, "blank", {"length": str(clip.timeline_start_frame-cursor)})
                rate = (asset_rates or {}).get(clip.asset_id, (plan.output.fps_num, plan.output.fps_den))
                source_in = round(clip.source_in_frame*rate[1]/rate[0]*plan.output.fps_num/plan.output.fps_den)
                ET.SubElement(playlist, "entry", {"producer": producer_ids[clip.id], "in": str(source_in),
                    "out": str(source_in+clip.duration_frames-1)})
                cursor = clip.timeline_start_frame+clip.duration_frames
        tractor = ET.SubElement(root, "tractor", {"id": f"video_track_{track}", "in": "0", "out": str(end-1)})
        ET.SubElement(tractor, "track", {"producer": f"video_playlist_{track}_0"})
        ET.SubElement(tractor, "track", {"producer": f"video_playlist_{track}_1"})
        for clip in lane_clips[1]:
            segments: list[tuple[int, int, str | None, bool]] = []
            cursor = clip.timeline_start_frame
            for transition in sorted((t for t in plan.transitions if clip.id in {t.from_clip, t.to_clip}),
                                     key=lambda t: next(c.timeline_start_frame for c in clips if c.id == t.to_clip)):
                incoming = transition.to_clip == clip.id
                start = clip.timeline_start_frame if incoming else clip.timeline_start_frame + clip.duration_frames - transition.duration_frames
                stop = start + transition.duration_frames
                if cursor < start:
                    segments.append((cursor, start, None, False))
                segments.append((start, stop, transition.type, incoming))
                cursor = stop
            if cursor < clip.timeline_start_frame+clip.duration_frames:
                segments.append((cursor, clip.timeline_start_frame+clip.duration_frames, None, False))
            for start, stop, kind, incoming in segments:
                compositor = ET.SubElement(tractor, "transition", {"in": str(start), "out": str(stop-1)})
                prop(compositor, "mlt_service", "composite")
                prop(compositor, "a_track", 0)
                prop(compositor, "b_track", 1)
                prop(compositor, "progressive", 1)
                prop(compositor, "distort", 1)
                length = max(1, stop-start-1)
                if kind == "slide":
                    first, last = (width, 0) if incoming else (0, -width)
                    geometry = f"0={first}/0:{width}x{height}:1;{length}={last}/0:{width}x{height}:1"
                elif kind:
                    first, last = (0, 1) if incoming else (1, 0)
                    geometry = f"0=0/0:{width}x{height}:{first};{length}=0/0:{width}x{height}:{last}"
                else:
                    geometry = f"0/0:{width}x{height}:1"
                prop(compositor, "geometry", geometry)
                if kind == "wipe":
                    prop(compositor, "luma", wipe_path)
                    prop(compositor, "softness", 0.01)
        mix = ET.SubElement(tractor, "transition", {"in": "0", "out": str(end-1)})
        for name, value in {"mlt_service": "mix", "a_track": 0, "b_track": 1, "always_active": 1, "sum": 1}.items():
            prop(mix, name, value)
        track_ids.append(f"video_track_{track}")
    main = ET.SubElement(root, "tractor", {"id": "main", "in": "0", "out": str(end-1)})
    for identity in ["background", *track_ids, *audio_ids]:
        ET.SubElement(main, "track", {"producer": identity})
    for index in range(1, len(track_ids)+len(audio_ids)+1):
        if index <= len(track_ids):
            composite = ET.SubElement(main, "transition", {"in": "0", "out": str(end-1)})
            for name, value in {"mlt_service": "composite", "a_track": 0, "b_track": index,
                                "geometry": f"0/0:{width}x{height}:1", "progressive": 1}.items():
                prop(composite, name, value)
        mix = ET.SubElement(main, "transition", {"in": "0", "out": str(end-1)})
        for name, value in {"mlt_service": "mix", "a_track": 0, "b_track": index, "always_active": 1, "sum": 1}.items():
            prop(mix, name, value)
    project = workdir / "timeline.mlt"
    ET.ElementTree(root).write(project, encoding="utf-8", xml_declaration=True)
    ET.parse(project)
    return project


async def render(plan: TimelinePlan, asset_paths: dict[UUID, Path], output_path: Path,
                 asset_rates: dict[UUID, tuple[int, int]] | None = None,
                 cancelled: asyncio.Event | None = None) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="autocut-mlt-") as temporary:
        work = Path(temporary)
        prepared, paths = await prepare(plan, asset_paths, work, asset_rates or {}, cancelled)
        project = build_mlt_xml(prepared, paths, work)
        target = work / "composition.mp4" if plan.titles else output_path
        args = [get_settings().mlt_render_binary, "-silent", str(project), "-consumer",
                f"avformat:{target}", "vcodec=libx264", "acodec=aac", "f=mp4", "threads=2",
                "real_time=-2", "crf=23" if plan.output.preset == "preview" else "crf=18",
                "preset=fast", "pix_fmt=yuv420p", "ar=48000", "ac=2", "movflags=+faststart"]
        code, _, error = await run_media_command(args, cancelled=cancelled)
        if code or not target.is_file() or not target.stat().st_size:
            raise ProcessError("render_failed", "MLT could not render the timeline", 422,
                               details=error.decode(errors="replace")[-1500:])
        if plan.titles:
            await overlay_titles(target, output_path, plan, work, cancelled)
