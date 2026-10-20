import shutil
import subprocess
from pathlib import Path

import pytest

from app.modules.rendering.media_probe import generate_proxy, generate_thumbnail, probe

pytestmark = pytest.mark.media


@pytest.mark.asyncio
async def test_probe_thumbnail_and_proxy_on_generated_media(tmp_path: Path):
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        pytest.skip("ffmpeg executable is unavailable")
    source = tmp_path / "synthetic.mp4"
    subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            "testsrc=size=320x240:rate=24",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:sample_rate=44100",
            "-t",
            "1",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-y",
            str(source),
        ],
        check=True,
        timeout=30,
    )
    metadata = await probe(source)
    assert metadata["width"] == 320 and metadata["height"] == 240
    assert metadata["has_audio"] is True
    thumbnail, proxy = tmp_path / "thumb.jpg", tmp_path / "proxy.mp4"
    await generate_thumbnail(source, thumbnail)
    await generate_proxy(source, proxy)
    assert thumbnail.stat().st_size > 0
    assert (await probe(proxy))["media_type"] == "video"
