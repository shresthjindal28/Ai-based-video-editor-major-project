from pathlib import Path

from app.core.config import get_settings
from app.core.exceptions import ProcessError
from app.modules.editor.schemas import TimelinePlan
from app.modules.rendering.media_probe import probe, run_media_command


async def verify_render(path: Path, plan: TimelinePlan) -> dict:
    if not path.is_file() or path.stat().st_size <= 0:
        raise ProcessError("qc_missing_output", "Rendered output is missing or empty", 422)
    info = await probe(path)
    if (
        info["media_type"] != "video"
        or info["width"] != plan.output.width
        or info["height"] != plan.output.height
    ):
        raise ProcessError(
            "qc_profile_mismatch", "Rendered dimensions do not match the requested output", 422
        )
    expected = (
        max(
            [c.timeline_start_frame + c.duration_frames for c in plan.clips]
            + [a.timeline_start_frame + a.duration_frames for a in plan.audio]
        )
        * plan.output.fps_den
        / plan.output.fps_num
    )
    if abs(info["duration"] - expected) > max(0.25, 2 * plan.output.fps_den / plan.output.fps_num):
        raise ProcessError(
            "qc_duration_mismatch", "Rendered duration differs from the requested timeline", 422
        )
    if get_settings().decode_check:
        code, _, _ = await run_media_command(
            [get_settings().ffmpeg_binary, "-v", "error", "-i", str(path), "-f", "null", "-"],
            timeout=get_settings().process_timeout_seconds,
        )
        if code:
            raise ProcessError("qc_decode_failed", "Rendered output did not fully decode", 422)
    return info
