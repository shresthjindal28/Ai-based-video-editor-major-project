from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.exceptions import DomainError
from app.modules.editor.compiler import compile_plan
from app.modules.editor.schemas import AudioClipSpec, ClipSpec, EffectSpec, OutputProfile, TimelinePlan, TransitionSpec
from app.modules.editor.validators import validate_plan


class AssetsSession:
    def __init__(self,asset):
        self.asset=asset
    async def scalars(self,query):
        return SimpleNamespace(all=lambda:[self.asset])


@pytest.fixture
def contract():
    owner,project,asset_id=uuid4(),uuid4(),uuid4()
    asset=SimpleNamespace(id=asset_id,duration=2.0,fps_num=24,fps_den=1,media_type="video",has_audio=True)
    plan=TimelinePlan(project_id=project,output=OutputProfile(width=640,height=360,fps_num=24,preset="preview"),
        clips=[ClipSpec(id=uuid4(),asset_id=asset_id,source_in_frame=0,duration_frames=48,timeline_start_frame=0)])
    return AssetsSession(asset),owner,project,plan


@pytest.mark.asyncio
async def test_valid_frame_ranges(contract):
    session,owner,project,plan=contract
    await validate_plan(session,owner,project,plan)


@pytest.mark.asyncio
async def test_source_range_is_rejected(contract):
    session,owner,project,plan=contract
    plan.clips[0].source_in_frame=24
    with pytest.raises(DomainError) as error:
        await validate_plan(session,owner,project,plan)
    assert error.value.code == "source_range_invalid"


@pytest.mark.parametrize("effect",[
    EffectSpec(id="brightness",parameters={"value":2}),
    EffectSpec(id="blur",parameters={"sigma":-1}),
    EffectSpec(id="lut",parameters={"name":"/private/arbitrary.cube"}),
    EffectSpec(id="fade_in",parameters={"frames":49}),
])
@pytest.mark.asyncio
async def test_effect_ranges_and_lut_paths_are_rejected(contract,effect):
    session,owner,project,plan=contract
    plan.clips[0].effects=[effect]
    with pytest.raises(DomainError) as error:
        await validate_plan(session,owner,project,plan)
    assert error.value.code == "effect_parameters_invalid"


@pytest.mark.asyncio
async def test_transition_requires_exact_overlap(contract):
    session,owner,project,plan=contract
    first=plan.clips[0]
    second=first.model_copy(update={"id":uuid4(),"timeline_start_frame":24})
    plan.clips.append(second)
    plan.transitions=[TransitionSpec(from_clip=first.id,to_clip=second.id,type="wipe",duration_frames=12)]
    with pytest.raises(DomainError) as error:
        await validate_plan(session,owner,project,plan)
    assert error.value.code == "transition_invalid"


def test_compiler_converts_native_frame_rates_and_includes_audio(contract):
    _,_,_,plan=contract
    clip=plan.clips[0]
    clip.duration_frames=24
    plan.audio=[AudioClipSpec(asset_id=clip.asset_id,duration_frames=72)]
    compiled=compile_plan(plan,{clip.asset_id:(30,1)})
    assert compiled.clips[0].source_out_frame==29
    assert compiled.duration_frames==72
    assert compiled.audio


def test_ntsc_rational_profile_is_supported():
    profile=OutputProfile(width=1920,height=1080,fps_num=30000,fps_den=1001)
    assert profile.fps_num/profile.fps_den == pytest.approx(29.97003)
