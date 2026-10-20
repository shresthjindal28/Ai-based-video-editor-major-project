from __future__ import annotations

import asyncio
import json
import logging
import math
import os
import shutil
import signal
import sys
from fractions import Fraction
from pathlib import Path

from app.core.config import get_settings
from app.core.exceptions import ProcessError
from app.core.metrics import PROCESSES

logger = logging.getLogger(__name__)
_process_slots = asyncio.Semaphore(get_settings().max_media_processes)


async def run_media_command(
    args: list[str], timeout: int | None = None, cancelled: asyncio.Event | None = None
) -> tuple[int, bytes, bytes]:
    async with _process_slots:
        if cancelled and cancelled.is_set():
            raise ProcessError("job_cancelled", "Media processing cancelled", 409)
        return await _run_media_command(args, timeout, cancelled)


async def _run_media_command(
    args: list[str], timeout: int | None, cancelled: asyncio.Event | None
) -> tuple[int, bytes, bytes]:
    process = None
    try:
        if shutil.which(args[0]) is None:
            raise FileNotFoundError(args[0])
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "app.modules.rendering.process_guard", str(os.getpid()), *args,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            start_new_session=True,
        )
        async def drain(stream, limit: int) -> bytes:
            retained = bytearray()
            while chunk := await stream.read(65536):
                retained.extend(chunk)
                if len(retained) > limit:
                    del retained[:-limit]
            return bytes(retained)

        output_task = asyncio.create_task(drain(process.stdout, 4 * 1024**2))
        error_task = asyncio.create_task(drain(process.stderr, 256 * 1024))
        deadline = asyncio.get_running_loop().time() + (timeout or get_settings().process_timeout_seconds)
        while process.returncode is None:
            if cancelled and cancelled.is_set():
                raise ProcessError("job_cancelled", "Media processing cancelled", 409)
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                raise TimeoutError()
            try:
                await asyncio.wait_for(process.wait(), min(0.25, remaining))
            except TimeoutError:
                continue
        stdout, stderr = await asyncio.gather(output_task, error_task)
    except TimeoutError as exc:
        raise ProcessError(
            "media_timeout", "Media processing exceeded its time limit", 422
        ) from exc
    except FileNotFoundError as exc:
        raise ProcessError(
            "media_tool_missing", f"Required media tool is unavailable: {Path(args[0]).name}", 503
        ) from exc
    finally:
        if process is not None and process.returncode is None:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                await process.wait()
            try:
                await asyncio.wait_for(process.wait(), 5)
            except TimeoutError:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    await process.wait()
                await process.wait()
        if "output_task" in locals():
            await asyncio.gather(output_task, error_task, return_exceptions=True)
    PROCESSES.labels(
        tool=Path(args[0]).name, outcome="success" if process.returncode == 0 else "failure"
    ).inc()
    if process.returncode and b"No space left on device" in stderr:
        raise ProcessError("storage_full", "Media storage capacity is exhausted", 507)
    return process.returncode or 0, stdout, stderr


async def probe(path: Path) -> dict:
    code, output, _ = await run_media_command(
        [
            get_settings().ffprobe_binary,
            "-v",
            "error",
            "-protocol_whitelist",
            "file,pipe",
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
    format_name = data.get("format", {}).get("format_name", "")
    allowed_formats = {"mov,mp4,m4a,3gp,3g2,mj2", "matroska,webm", "mp3", "wav", "aac", "flac"}
    if format_name not in allowed_formats:
        raise ProcessError("unsupported_media", "Unsupported media container", 415)
    video = next((stream for stream in streams if stream.get("codec_type") == "video"
                  and not stream.get("disposition", {}).get("attached_pic")), None)
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
    if not math.isfinite(duration) or duration <= 0 or duration > get_settings().max_project_duration_seconds:
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
        "mime_type": ({"matroska,webm": "video/webm", "wav": "audio/wav", "flac": "audio/flac",
                       "aac": "audio/aac", "mp3": "audio/mpeg"}.get(format_name, "video/mp4" if video else "audio/mp4")),
        "rotation": next(
            (
                int(x.get("rotation", 0))
                for x in (video or {}).get("side_data_list", [])
                if "rotation" in x
            ),
            0,
        ),
    }


async def generate_thumbnail(source: Path, destination: Path, at_seconds: float = 0.5,
                             cancelled: asyncio.Event | None = None) -> None:
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
        cancelled=cancelled,
    )
    if code or not destination.is_file() or destination.stat().st_size == 0:
        destination.unlink(missing_ok=True)
        raise ProcessError("thumbnail_failed", "Thumbnail generation failed", 422)


async def generate_proxy(source: Path, destination: Path, cancelled: asyncio.Event | None = None) -> None:
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
        cancelled=cancelled,
    )
    if code or not destination.is_file() or destination.stat().st_size == 0:
        destination.unlink(missing_ok=True)
        raise ProcessError("proxy_failed", "Proxy generation failed", 422)
