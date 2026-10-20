"""Deterministic, bounded FFmpeg intermediates for MLT compositing.

Only validated contract values are interpolated into filters. Media paths are
arguments, and title text is read from a private UTF-8 file, never filter syntax.
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from uuid import NAMESPACE_URL, UUID, uuid5

from app.core.config import get_settings
from app.core.exceptions import ProcessError
from app.modules.editor.schemas import TimelinePlan
from app.modules.rendering.media_probe import probe, run_media_command


def animate(initial: float, keyframes, variable: str) -> str:
    points = [(0, float(initial))]
    for key in keyframes:
        if key.frame == 0:
            points[0] = (0, key.value)
        else:
            points.append((key.frame, key.value))
    expression = str(points[-1][1])
    for (start, first), (end, last) in reversed(list(zip(points, points[1:], strict=False))):
        expression = f"if(lt({variable},{end}),{first}+({last}-{first})*({variable}-{start})/{end-start},{expression})"
    return expression


def write_lut(path: Path, name: str) -> None:
    # Small, deterministic creative LUTs. No user filesystem paths are accepted.
    red, blue = (1.08, 0.92) if name == "warm" else (0.92, 1.08)
    lines = ['TITLE "AutoCut creative LUT"', "LUT_3D_SIZE 2", "DOMAIN_MIN 0 0 0", "DOMAIN_MAX 1 1 1"]
    for b in (0, 1):
        for g in (0, 1):
            for r in (0, 1):
                lines.append(f"{min(1, r*red):.6f} {g:.6f} {min(1, b*blue):.6f}")
    path.write_text("\n".join(lines) + "\n")


async def prepare(plan: TimelinePlan, assets: dict[UUID, Path], work: Path,
                  rates: dict[UUID, tuple[int, int]], cancelled: asyncio.Event | None):
    fps = plan.output.fps_num / plan.output.fps_den
    width, height = plan.output.width, plan.output.height
    clips, audio_tracks, paths = [], [], {}
    for clip in plan.clips:
        source = assets[clip.asset_id]
        info = await probe(source)
        rate = rates.get(clip.asset_id, (plan.output.fps_num, plan.output.fps_den))
        start = clip.source_in_frame * rate[1] / rate[0]
        target = work / f"clip-{clip.id.hex}.mp4"
        scale_mode = "decrease" if plan.output.fit == "contain" else "increase"
        vf = [f"fps={plan.output.fps_num}/{plan.output.fps_den}",
              f"scale={width}:{height}:force_original_aspect_ratio={scale_mode}"]
        if scale_mode == "decrease":
            vf.append(f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black")
        else:
            vf.append(f"crop={width}:{height}")
        vf.append("setsar=1")
        camera = {effect.id: effect for effect in clip.effects if effect.id in {"zoom", "pan", "tilt"}}
        if camera:
            expressions = {}
            for name, default in (("zoom", 1), ("pan", 0), ("tilt", 0)):
                effect = camera.get(name)
                expressions[name] = animate(effect.parameters["value"], effect.keyframes, "on") if effect else str(default)
            vf.append(f"zoompan=z='{expressions['zoom']}':x='(iw-iw/zoom)*(({expressions['pan']})+1)/2':y='(ih-ih/zoom)*(({expressions['tilt']})+1)/2':d=1:s={width}x{height}:fps={plan.output.fps_num}/{plan.output.fps_den}")
        for effect in clip.effects:
            params = effect.parameters
            if effect.id in {"brightness", "contrast", "saturation"}:
                vf.append(f"eq={effect.id}={float(params['value'])}")
            elif effect.id == "blur":
                if params["sigma"] > 0:
                    vf.append(f"gblur=sigma={float(params['sigma'])}")
            elif effect.id == "color":
                vf.append(f"colorbalance=rs={float(params['red'])}:gs={float(params['green'])}:bs={float(params['blue'])}")
            elif effect.id in {"fade_in", "fade_out"}:
                frames = params["frames"]
                start_frame = 0 if effect.id == "fade_in" else clip.duration_frames - frames
                vf.append(f"fade=t={'in' if effect.id == 'fade_in' else 'out'}:start_frame={start_frame}:nb_frames={frames}")
            elif effect.id == "lut":
                lut = work / f"{params['name']}.cube"
                write_lut(lut, params["name"])
                vf.append(f"lut3d=file={lut}")
        vf.extend(["tpad=stop_mode=clone:stop_duration=0.1", "format=yuv420p"])
        volume = animate(clip.volume, clip.volume_keyframes, f"t*{fps}")
        af = [f"volume='{volume}':eval=frame"]
        for transition in plan.transitions:
            duration = transition.duration_frames / fps
            if transition.to_clip == clip.id:
                af.append(f"afade=t=in:d={duration}")
            if transition.from_clip == clip.id:
                af.append(f"afade=t=out:st={(clip.duration_frames-transition.duration_frames)/fps}:d={duration}")
        af.extend(["apad", f"atrim=duration={clip.duration_frames/fps}", "aresample=48000"])
        args = [get_settings().ffmpeg_binary, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
                "-ss", str(start), "-i", str(source)]
        if not info["has_audio"]:
            args += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
        args += ["-map", "0:v:0", "-map", "0:a:0" if info["has_audio"] else "1:a:0",
                 "-vf", ",".join(vf), "-af", ",".join(af),
                 "-frames:v", str(clip.duration_frames), "-t", str(clip.duration_frames/fps),
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-threads", "2",
                 "-c:a", "aac", "-ac", "2", str(target)]
        code, _, error = await run_media_command(args, cancelled=cancelled)
        if code:
            raise ProcessError("clip_processing_failed", "Could not prepare timeline clip", 422, details=error.decode(errors="replace")[-1500:])
        paths[clip.id] = target
        clips.append(clip.model_copy(update={"asset_id": clip.id, "source_in_frame": 0,
                                            "effects": [], "volume": 1, "volume_keyframes": []}))
    for index, audio in enumerate(plan.audio):
        rate = rates.get(audio.asset_id, (plan.output.fps_num, plan.output.fps_den))
        start = audio.source_in_frame * rate[1] / rate[0]
        target = work / f"audio-{index}.wav"
        af = [f"volume={audio.gain}"]
        if audio.fade_in_frames:
            af.append(f"afade=t=in:d={audio.fade_in_frames/fps}")
        if audio.fade_out_frames:
            af.append(f"afade=t=out:st={(audio.duration_frames-audio.fade_out_frames)/fps}:d={audio.fade_out_frames/fps}")
        code, _, error = await run_media_command([get_settings().ffmpeg_binary, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
            "-ss", str(start), "-i", str(assets[audio.asset_id]), "-t", str(audio.duration_frames/fps),
            "-vn", "-af", ",".join(af), "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", str(target)], cancelled=cancelled)
        if code:
            raise ProcessError("audio_processing_failed", "Could not prepare audio track", 422, details=error.decode(errors="replace")[-1500:])
        identity = uuid5(NAMESPACE_URL, f"autocut:audio:{index}")
        paths[identity] = target
        audio_tracks.append(audio.model_copy(update={"asset_id": identity, "source_in_frame": 0,
            "gain": 1, "fade_in_frames": 0, "fade_out_frames": 0}))
    return plan.model_copy(update={"clips": clips, "audio": audio_tracks}), paths


async def overlay_titles(source: Path, output: Path, plan: TimelinePlan, work: Path,
                         cancelled: asyncio.Event | None) -> None:
    filters = []
    for index, title in enumerate(plan.titles):
        path = work / f"title-{index}.txt"
        path.write_text(title.text)
        y = {"top": "h*0.08", "center": "(h-text_h)/2", "bottom": "h*0.9-text_h"}[title.position]
        end = title.start_frame + title.duration_frames - 1
        filters.append(f"drawtext=textfile={path}:expansion=none:fontsize={title.font_size}:fontcolor={title.color}:x=(w-text_w)/2:y={y}:enable='between(n,{title.start_frame},{end})'")
    code, _, error = await run_media_command([get_settings().ffmpeg_binary, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
        "-i", str(source), "-vf", ",".join(filters), "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-threads", "2",
        "-c:a", "copy", "-movflags", "+faststart", str(output)], cancelled=cancelled)
    if code:
        raise ProcessError("title_processing_failed", "Title rendering failed; FFmpeg drawtext support is required", 422, details=error.decode(errors="replace")[-1500:])
