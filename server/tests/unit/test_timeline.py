from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.modules.editor.compiler import compile_plan
from app.modules.editor.schemas import ClipSpec, OutputProfile, TimelinePlan
from app.modules.rendering.mlt_engine import build_mlt_xml


def plan() -> TimelinePlan:
    project_id, asset_id = uuid4(), uuid4()
    return TimelinePlan(
        project_id=project_id,
        output=OutputProfile(width=1920, height=1080),
        clips=[
            ClipSpec(
                id=uuid4(),
                asset_id=asset_id,
                source_in_frame=12,
                duration_frames=48,
                timeline_start_frame=0,
            ),
            ClipSpec(
                id=uuid4(),
                asset_id=asset_id,
                source_in_frame=80,
                duration_frames=24,
                timeline_start_frame=48,
            ),
        ],
    )


def test_compiler_uses_inclusive_source_out_and_stable_order():
    compiled = compile_plan(plan())
    assert compiled.duration_frames == 72
    assert compiled.clips[0].source_out_frame == 59
    assert compiled.clips[1].timeline_start_frame == 48


def test_output_profile_rejects_arbitrary_resolution():
    with pytest.raises(ValidationError):
        OutputProfile(width=1111, height=777)


def test_mlt_xml_is_structured_and_resolves_only_supplied_assets(tmp_path: Path):
    edit = plan()
    asset_id = edit.clips[0].asset_id
    media = tmp_path / 'source "quoted" & escaped.mp4'
    media.touch()
    project = build_mlt_xml(edit, {asset_id: media}, tmp_path)
    contents = project.read_text()
    assert "&amp;" in contents
    assert "video_playlist_0_0" in contents
    assert "../" not in contents


def test_camera_keyframes_reject_unsorted_and_out_of_range_frames():
    from app.modules.editor.schemas import Keyframe
    with pytest.raises(ValidationError):
        ClipSpec(id=uuid4(),asset_id=uuid4(),source_in_frame=0,duration_frames=24,timeline_start_frame=0,
                 volume_keyframes=[Keyframe(frame=12,value=1),Keyframe(frame=2,value=0)])
