from __future__ import annotations

import asyncio
import logging
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from uuid import UUID

from app.core.config import get_settings
from app.core.exceptions import ProcessError
from app.modules.editor.schemas import TimelinePlan

logger = logging.getLogger(__name__)


def _frames_as_seconds(frames: int, fps: float) -> str:
    return f"{frames / fps:.6f}"


def build_mlt_xml(
    plan: TimelinePlan,
    assets: dict[UUID, Path],
    workdir: Path,
    asset_rates: dict[UUID, tuple[int, int]] | None = None,
) -> Path:
    """Compile a validated frame timeline into an MLT XML composition."""
    profile = plan.output
    fps = profile.fps_num / profile.fps_den
    root = ET.Element("mlt", {"LC_NUMERIC": "C", "version": "7.0.0", "producer": "main"})
    ET.SubElement(
        root,
        "profile",
        {
            "description": "AutoCut",
            "width": str(profile.width),
            "height": str(profile.height),
            "frame_rate_num": str(profile.fps_num),
            "frame_rate_den": str(profile.fps_den),
            "progressive": "1",
            "sample_aspect_num": "1",
            "sample_aspect_den": "1",
            "display_aspect_num": str(profile.width),
            "display_aspect_den": str(profile.height),
            "colorspace": "709",
        },
    )

    video = sorted(
        plan.clips, key=lambda clip: (clip.track, clip.timeline_start_frame, str(clip.id))
    )
    lanes: dict[tuple[int, int], list] = {}
    lane_end: dict[tuple[int, int], int] = {}
    clip_lane: dict[UUID, tuple[int, int]] = {}
    for clip in video:
        candidates = [
            lane
            for lane in (0, 1)
            if lane_end.get((clip.track, lane), 0) <= clip.timeline_start_frame
        ]
        if not candidates:
            raise ProcessError(
                "timeline_complexity_unsupported",
                "MLT renderer supports at most two overlapping video clips per track",
                422,
            )
        lane_number = candidates[0]
        key = (clip.track, lane_number)
        lanes.setdefault(key, []).append(clip)
        lane_end[key] = clip.timeline_start_frame + clip.duration_frames
        clip_lane[clip.id] = key

    producers: dict[str, tuple[Path, int, int]] = {}
    for index, clip in enumerate(video):
        producer_id = f"video_{index}"
        producers[producer_id] = (assets[clip.asset_id], 0, 0)
    audio_producers = []
    for index, audio in enumerate(plan.audio):
        producer_id = f"audio_{index}"
        producers[producer_id] = (assets[audio.asset_id], -1, 0)
        audio_producers.append((producer_id, audio))

    for producer_id, (path, video_index, audio_index) in producers.items():
        producer = ET.SubElement(root, "producer", {"id": producer_id})
        ET.SubElement(producer, "property", {"name": "resource"}).text = str(path)
        ET.SubElement(producer, "property", {"name": "mlt_service"}).text = "avformat-novalidate"
        ET.SubElement(producer, "property", {"name": "video_index"}).text = str(video_index)
        ET.SubElement(producer, "property", {"name": "audio_index"}).text = str(audio_index)

    playlist_tracks: dict[tuple[int, int], str] = {}
    for track in sorted({key[0] for key in lanes}):
        for lane in (0, 1):
            key = (track, lane)
            if key not in lanes:
                continue
            playlist_id = f"video_playlist_{track}_{lane}"
            playlist_tracks[key] = playlist_id
            playlist = ET.SubElement(root, "playlist", {"id": playlist_id})
            cursor = 0
            for clip in lanes[key]:
                if clip.timeline_start_frame > cursor:
                    ET.SubElement(
                        playlist,
                        "blank",
                        {"length": _frames_as_seconds(clip.timeline_start_frame - cursor, fps)},
                    )
                producer_id = f"video_{video.index(clip)}"
                source_rate = (asset_rates or {}).get(
                    clip.asset_id, (profile.fps_num, profile.fps_den)
                )
                source_fps = source_rate[0] / source_rate[1]
                # MLT uses the profile timebase for in/out; convert source frame position to seconds,
                # then to the output timebase to preserve the requested source time.
                source_in = round(clip.source_in_frame / source_fps * fps)
                source_len = clip.duration_frames
                entry = ET.SubElement(
                    playlist,
                    "entry",
                    {
                        "producer": producer_id,
                        "in": str(source_in),
                        "out": str(source_in + source_len - 1),
                    },
                )
                for effect in clip.effects:
                    filter_element = ET.SubElement(entry, "filter")
                    service = (
                        effect.id
                        if effect.id in {"brightness", "contrast", "saturation"}
                        else "affine"
                        if effect.id in {"zoom", "pan", "tilt"}
                        else "boxblur"
                    )
                    ET.SubElement(
                        filter_element, "property", {"name": "mlt_service"}
                    ).text = service
                    if service in {"brightness", "contrast", "saturation"}:
                        ET.SubElement(filter_element, "property", {"name": "level"}).text = str(
                            effect.parameters["value"]
                        )
                    elif service == "affine":
                        zoom = (
                            float(effect.parameters.get("value", 1.0))
                            if effect.id == "zoom"
                            else 1.0
                        )
                        pan = (
                            float(effect.parameters.get("value", 0.0))
                            if effect.id == "pan"
                            else 0.0
                        )
                        tilt = (
                            float(effect.parameters.get("value", 0.0))
                            if effect.id == "tilt"
                            else 0.0
                        )
                        width, height = profile.width / zoom, profile.height / zoom
                        x, y = (
                            (profile.width - width) / 2 + pan * width / 2,
                            (profile.height - height) / 2 + tilt * height / 2,
                        )
                        ET.SubElement(
                            filter_element, "property", {"name": "transition.rect"}
                        ).text = f"{x:.3f} {y:.3f} {width:.3f} {height:.3f} 1"
                    else:
                        ET.SubElement(
                            filter_element, "property", {"name": "luma_radius"}
                        ).text = str(round(effect.parameters["sigma"]))
                if clip.volume != 1 or clip.volume_keyframes:
                    filter_element = ET.SubElement(entry, "filter")
                    ET.SubElement(
                        filter_element, "property", {"name": "mlt_service"}
                    ).text = "volume"
                    keyframes = [f"0={clip.volume}"] + [
                        f"{frame.frame}={frame.value}" for frame in clip.volume_keyframes
                    ]
                    ET.SubElement(filter_element, "property", {"name": "level"}).text = ";".join(keyframes)
                cursor = clip.timeline_start_frame + clip.duration_frames

    audio_playlist_ids = []
    for index, (producer_id, audio) in enumerate(audio_producers):
        playlist_id = f"audio_playlist_{index}"
        playlist = ET.SubElement(root, "playlist", {"id": playlist_id})
        if audio.timeline_start_frame:
            ET.SubElement(
                playlist, "blank", {"length": _frames_as_seconds(audio.timeline_start_frame, fps)}
            )
        source_rate = (asset_rates or {}).get(audio.asset_id, (profile.fps_num, profile.fps_den))
        source_fps = source_rate[0] / source_rate[1]
        source_in = round(audio.source_in_frame / source_fps * fps)
        source_out = source_in + audio.duration_frames - 1
        entry = ET.SubElement(
            playlist,
            "entry",
            {"producer": producer_id, "in": str(source_in), "out": str(source_out)},
        )
        volume_filter = ET.SubElement(entry, "filter")
        ET.SubElement(volume_filter, "property", {"name": "mlt_service"}).text = "volume"
        ET.SubElement(volume_filter, "property", {"name": "level"}).text = str(audio.gain)
        if audio.fade_in_frames:
            fade = ET.SubElement(entry, "filter")
            ET.SubElement(fade, "property", {"name": "mlt_service"}).text = "volume"
            ET.SubElement(
                fade, "property", {"name": "level"}
            ).text = f"0=0;{audio.fade_in_frames}={audio.gain}"
        if audio.fade_out_frames:
            fade = ET.SubElement(entry, "filter")
            ET.SubElement(fade, "property", {"name": "mlt_service"}).text = "volume"
            ET.SubElement(
                fade, "property", {"name": "level"}
            ).text = f"{audio.duration_frames - audio.fade_out_frames}={audio.gain};{audio.duration_frames}=0"
        audio_playlist_ids.append(playlist_id)

    max_frame = max(
        [clip.timeline_start_frame + clip.duration_frames for clip in plan.clips]
        + [track.timeline_start_frame + track.duration_frames for track in plan.audio]
    )
    tractor = ET.SubElement(
        root, "tractor", {"id": "main", "in": "0", "out": str(max(0, max_frame - 1))}
    )
    track_index: dict[tuple[int, int], int] = {}
    for key, playlist_id in playlist_tracks.items():
        track_index[key] = len(track_index)
        ET.SubElement(tractor, "track", {"producer": playlist_id})
    for playlist_id in audio_playlist_ids:
        ET.SubElement(tractor, "track", {"producer": playlist_id})
    for transition in plan.transitions:
        left, right = (
            next(c for c in video if c.id == transition.from_clip),
            next(c for c in video if c.id == transition.to_clip),
        )
        a, b = clip_lane[left.id], clip_lane[right.id]
        trans = ET.SubElement(
            tractor,
            "transition",
            {
                "in": str(right.timeline_start_frame),
                "out": str(right.timeline_start_frame + transition.duration_frames - 1),
            },
        )
        ET.SubElement(trans, "property", {"name": "a_track"}).text = str(track_index[a])
        ET.SubElement(trans, "property", {"name": "b_track"}).text = str(track_index[b])
        ET.SubElement(trans, "property", {"name": "mlt_service"}).text = "luma"
        ET.SubElement(trans, "property", {"name": "always_active"}).text = "1"
    for index in range(len(audio_playlist_ids)):
        mix = ET.SubElement(tractor, "transition")
        ET.SubElement(mix, "property", {"name": "a_track"}).text = "0"
        ET.SubElement(mix, "property", {"name": "b_track"}).text = str(len(playlist_tracks) + index)
        ET.SubElement(mix, "property", {"name": "mlt_service"}).text = "mix"
        ET.SubElement(mix, "property", {"name": "always_active"}).text = "1"
    project = workdir / "timeline.mlt"
    ET.ElementTree(root).write(project, encoding="utf-8", xml_declaration=True)
    ET.parse(project)
    return project


async def render(
    plan: TimelinePlan,
    asset_paths: dict[UUID, Path],
    output_path: Path,
    asset_rates: dict[UUID, tuple[int, int]] | None = None,
    cancelled: asyncio.Event | None = None,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="autocut-mlt-") as temp:
        project = build_mlt_xml(plan, asset_paths, Path(temp), asset_rates)
        args = [
            get_settings().mlt_render_binary,
            str(project),
            "-consumer",
            f"avformat:{output_path}",
            "vcodec=libx264",
            "acodec=aac",
            "f=mp4",
            "movflags=+faststart",
        ]
        try:
            process = await asyncio.create_subprocess_exec(
                *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            communicate = asyncio.create_task(process.communicate())
            remaining = get_settings().process_timeout_seconds
            while not communicate.done():
                if cancelled and cancelled.is_set():
                    process.terminate()
                    try:
                        await asyncio.wait_for(process.wait(), timeout=10)
                    except TimeoutError:
                        process.kill()
                        await process.wait()
                    raise ProcessError("job_cancelled", "Render was cancelled", 409)
                try:
                    await asyncio.wait_for(asyncio.shield(communicate), timeout=1)
                except TimeoutError:
                    remaining -= 1
                    if remaining <= 0:
                        process.kill()
                        await process.wait()
                        raise ProcessError(
                            "render_timeout", "Render exceeded its time limit", 422
                        ) from None
            _, stderr = communicate.result()
        except FileNotFoundError as exc:
            raise ProcessError(
                "mlt_unavailable", "MLT melt executable is required to render", 503
            ) from exc
        if process.returncode != 0:
            logger.error(
                "MLT render failed", extra={"operation": "mlt_render", "outcome": "failure"}
            )
            output_path.unlink(missing_ok=True)
            raise ProcessError(
                "render_failed",
                "MLT could not render this timeline",
                422,
                details=stderr.decode(errors="replace")[-1500:],
            )
        if not output_path.is_file() or output_path.stat().st_size == 0:
            raise ProcessError("render_empty", "MLT produced an empty output", 422)
