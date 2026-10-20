from __future__ import annotations

import asyncio
import json
import logging
from fractions import Fraction
from pathlib import Path

from app.core.config import get_settings
from app.core.exceptions import ProcessError
from app.core.metrics import PROCESSES

logger = logging.getLogger(__name__)


async def run_media_command(
    args: list[str], timeout: int | None = None
) -> tuple[int, bytes, bytes]:
    try:
        process = await asyncio.create_subprocess_exec(
            *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(
            process.communicate(), timeout or get_settings().process_timeout_seconds
        )
    except TimeoutError as exc:
        process.kill()
        await process.wait()
        raise ProcessError(
            "media_timeout", "Media processing exceeded its time limit", 422
        ) from exc
    except FileNotFoundError as exc:
        raise ProcessError(
            "media_tool_missing", f"Required media tool is unavailable: {Path(args[0]).name}", 503
        ) from exc
    PROCESSES.labels(
        tool=Path(args[0]).name, outcome="success" if process.returncode == 0 else "failure"
    ).inc()
    return process.returncode or 0, stdout, stderr


async def probe(path: Path) -> dict:
    code, output, _ = await run_media_command(
        [
            get_settings().ffprobe_binary,
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(path),
        ],
        timeout=60,
    )
    if code != 0:
        raise ProcessError("invalid_media", "The uploaded file is not valid supported media", 422)
    try:
        data = json.loads(output)
    except json.JSONDecodeError as exc:
        raise ProcessError("invalid_media_probe", "Could not read media metadata", 422) from exc
    streams = data.get("streams", [])
    video = next((stream for stream in streams if stream.get("codec_type") == "video"), None)
    audio = next((stream for stream in streams if stream.get("codec_type") == "audio"), None)
    if video is None and audio is None:
        raise ProcessError("unsupported_media", "Upload must contain video or audio", 415)
    try:
        fps = Fraction((video or {}).get("avg_frame_rate", "0/1"))
        duration = float(
            (data.get("format") or {}).get("duration", (video or audio or {}).get("duration", 0))
        )
    except (ValueError, ZeroDivisionError) as exc:
        raise ProcessError(
            "invalid_media_metadata", "Media stream metadata is malformed", 422
        ) from exc
    if duration <= 0 or duration > get_settings().max_project_duration_seconds:
        raise ProcessError(
            "unsupported_duration", "Media duration is invalid or exceeds the limit", 422
        )
    return {
        "media_type": "video" if video else "audio",
        "duration": duration,
        "width": int(video["width"]) if video else None,
        "height": int(video["height"]) if video else None,
        "fps_num": fps.numerator,
        "fps_den": fps.denominator,
        "video_codec": video.get("codec_name") if video else None,
        "audio_codec": audio.get("codec_name") if audio else None,
        "has_audio": audio is not None,
        "format_name": (data.get("format") or {}).get("format_name"),
        "mime_type": "video/mp4" if video else "audio/mpeg",
        "rotation": next(
            (
                int(x.get("rotation", 0))
                for x in (video or {}).get("side_data_list", [])
                if "rotation" in x
            ),
            0,
        ),
    }


async def generate_thumbnail(source: Path, destination: Path, at_seconds: float = 0.5) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    code, _, _ = await run_media_command(
        [
            get_settings().ffmpeg_binary,
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            str(max(0, at_seconds)),
            "-i",
            str(source),
            "-frames:v",
            "1",
            "-vf",
            "scale=640:-2",
            "-y",
            str(destination),
        ],
        timeout=120,
    )
    if code or not destination.is_file() or destination.stat().st_size == 0:
        destination.unlink(missing_ok=True)
        raise ProcessError("thumbnail_failed", "Thumbnail generation failed", 422)


async def generate_proxy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    code, _, _ = await run_media_command(
        [
            get_settings().ffmpeg_binary,
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(source),
            "-vf",
            "scale='min(960,iw)':-2",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "30",
            "-c:a",
            "aac",
            "-b:a",
            "96k",
            "-movflags",
            "+faststart",
            "-y",
            str(destination),
        ],
        timeout=get_settings().process_timeout_seconds,
    )
    if code or not destination.is_file() or destination.stat().st_size == 0:
        destination.unlink(missing_ok=True)
        raise ProcessError("proxy_failed", "Proxy generation failed", 422)
