import asyncio
import shutil
import subprocess
from uuid import uuid4

import pytest

from app.core.config import get_settings
from app.modules.editor.schemas import (
    AudioClipSpec,
    ClipSpec,
    EffectSpec,
    OutputProfile,
    TimelinePlan,
    TitleSpec,
    TransitionSpec,
)
from app.modules.rendering.media_probe import probe
from app.modules.rendering.mlt_engine import render
from app.modules.rendering.quality_control import verify_render

pytestmark = [pytest.mark.media, pytest.mark.mlt]


@pytest.fixture
def sources(tmp_path):
    paths = {}
    for color in ("red", "blue"):
        identity = uuid4()
        path = tmp_path / f"{color}.mp4"
        subprocess.run([get_settings().ffmpeg_binary, "-v", "error", "-f", "lavfi", "-i",
            f"color=c={color}:s=320x240:r=24", "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000",
            "-t", "1", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-y", str(path)], check=True, timeout=30)
        paths[identity] = path
    return paths


def require_mlt():
    if not shutil.which(get_settings().mlt_render_binary):
        pytest.skip("Configured MLT render executable is unavailable")


def frame(path, seconds=0.5):
    result = subprocess.run([get_settings().ffmpeg_binary, "-v", "error", "-ss", str(seconds), "-i", str(path),
        "-frames:v", "1", "-vf", "scale=16:16", "-pix_fmt", "rgb24", "-f", "rawvideo", "-"], capture_output=True, check=True, timeout=30)
    raw = result.stdout
    return tuple(sum(raw[c::3]) / (len(raw)//3) for c in range(3))


@pytest.mark.asyncio
async def test_mlt_trim_sequencing_and_source_audio(sources, tmp_path):
    require_mlt()
    ids = list(sources)
    plan = TimelinePlan(project_id=uuid4(), output=OutputProfile(width=640, height=360, fps_num=24, preset="preview"),
        clips=[ClipSpec(id=uuid4(), asset_id=identity, source_in_frame=6, duration_frames=12,
                        timeline_start_frame=index*12) for index, identity in enumerate(ids)])
    result = tmp_path / "sequence.mp4"
    await render(plan, sources, result, {i:(24,1) for i in ids})
    await verify_render(result, plan)
    first, last = frame(result, 0.2), frame(result, 0.7)
    assert first[0] > 100 and first[2] < 20
    assert last[2] > 100 and last[0] < 20


@pytest.mark.parametrize("kind", ["cross_dissolve", "wipe", "slide"])
@pytest.mark.asyncio
async def test_transitions_have_a_real_intermediate_image(sources, tmp_path, kind):
    require_mlt()
    ids = list(sources)
    clips = [ClipSpec(id=uuid4(), asset_id=identity, source_in_frame=0, duration_frames=24,
                      timeline_start_frame=index*12) for index, identity in enumerate(ids)]
    plan = TimelinePlan(project_id=uuid4(), output=OutputProfile(width=640, height=360, fps_num=24, preset="preview"),
        clips=clips, transitions=[TransitionSpec(from_clip=clips[0].id, to_clip=clips[1].id, type=kind, duration_frames=12)])
    result = tmp_path / f"{kind}.mp4"
    await render(plan, sources, result, {i:(24,1) for i in ids})
    await verify_render(result, plan)
    mid = frame(result, 0.75)
    assert mid[0] > 30 and mid[2] > 30, mid


@pytest.mark.parametrize("effect", [
    {"id":"brightness", "parameters":{"value":0.1}},
    {"id":"contrast", "parameters":{"value":1.2}},
    {"id":"saturation", "parameters":{"value":0.5}},
    {"id":"blur", "parameters":{"sigma":2}},
    {"id":"zoom", "parameters":{"value":1.2}, "keyframes":[{"frame":12,"value":1.5}]},
    {"id":"pan", "parameters":{"value":0.2}},
    {"id":"tilt", "parameters":{"value":-0.2}},
    {"id":"color", "parameters":{"red":0.1,"green":0,"blue":0}},
    {"id":"fade_in", "parameters":{"frames":6}},
    {"id":"fade_out", "parameters":{"frames":6}},
    {"id":"lut", "parameters":{"name":"warm"}},
])
@pytest.mark.asyncio
async def test_each_advertised_video_effect_executes(sources, tmp_path, effect):
    require_mlt()
    identity = next(iter(sources))
    plan = TimelinePlan(project_id=uuid4(), output=OutputProfile(width=640,height=360,fps_num=24,preset="preview"),
        clips=[ClipSpec(id=uuid4(),asset_id=identity,source_in_frame=0,duration_frames=24,timeline_start_frame=0,
                        effects=[EffectSpec.model_validate(effect)])])
    output = tmp_path / "effect.mp4"
    await render(plan, sources, output, {identity:(24,1)})
    await verify_render(output, plan)


@pytest.mark.asyncio
async def test_audio_mix_fades_and_titles_execute(sources, tmp_path):
    require_mlt()
    identity = next(iter(sources))
    plan = TimelinePlan(project_id=uuid4(),output=OutputProfile(width=640,height=360,fps_num=24,preset="preview"),
        clips=[ClipSpec(id=uuid4(),asset_id=identity,source_in_frame=0,duration_frames=24,timeline_start_frame=0,volume=0.5)],
        audio=[AudioClipSpec(asset_id=identity,duration_frames=24,gain=0.2,fade_in_frames=4,fade_out_frames=4)],
        titles=[TitleSpec(text="AutoCut % : ' safe text",start_frame=0,duration_frames=24)])
    output = tmp_path / "audio-titles.mp4"
    await render(plan,sources,output,{identity:(24,1)})
    assert (await probe(output))["has_audio"]
    await verify_render(output,plan)


@pytest.mark.asyncio
async def test_subprocess_cancel_terminates_render(sources, tmp_path):
    from app.core.exceptions import ProcessError
    require_mlt()
    identity = next(iter(sources))
    plan=TimelinePlan(project_id=uuid4(),output=OutputProfile(width=640,height=360,fps_num=24,preset="preview"),
        clips=[ClipSpec(id=uuid4(),asset_id=identity,source_in_frame=0,duration_frames=24,timeline_start_frame=0)])
    cancelled=asyncio.Event()
    cancelled.set()
    with pytest.raises(ProcessError, match="cancelled"):
        await render(plan,sources,tmp_path/"cancelled.mp4",{identity:(24,1)},cancelled)
