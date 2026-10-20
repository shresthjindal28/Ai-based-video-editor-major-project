from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DomainError
from app.modules.editor import repository
from app.modules.editor.models import EditRequest, EditVersion
from app.modules.editor.schemas import TimelinePlan
from app.modules.editor.validators import validate_plan
from app.modules.projects.service import require_project
from app.modules.timelines.models import TimelineItem


async def validate(
    session: AsyncSession, project_id: UUID, owner_id: UUID, plan: TimelinePlan
) -> None:
    await require_project(session, project_id, owner_id)
    await validate_plan(session, owner_id, project_id, plan)


async def create_version(
    session: AsyncSession,
    project_id: UUID,
    owner_id: UUID,
    plan: TimelinePlan,
    parent_id: UUID | None = None,
) -> EditVersion:
    await require_project(session, project_id, owner_id, lock=True)
    await validate_plan(session, owner_id, project_id, plan)
    if parent_id is not None:
        parent = await session.scalar(
            select(EditVersion).where(
                EditVersion.id == parent_id, EditVersion.project_id == project_id
            )
        )
        if parent is None:
            raise DomainError("version_not_found", "Parent edit version not found", 404)
    number = await repository.next_version(session, project_id)
    version = EditVersion(
        project_id=project_id,
        version_number=number,
        parent_version_id=parent_id,
        timeline=plan.model_dump(mode="json"),
        schema_version=plan.schema_version,
        validation_status="valid",
    )
    session.add(version)
    session.add(
        EditRequest(
            project_id=project_id,
            user_id=owner_id,
            request_type="structured",
            instructions=plan.model_dump(mode="json"),
            status="accepted",
        )
    )
    await session.flush()
    for clip in plan.clips:
        session.add(
            TimelineItem(
                version_id=version.id,
                asset_id=clip.asset_id,
                track=clip.track,
                start_frame=clip.timeline_start_frame,
                duration_frames=clip.duration_frames,
            )
        )
    for index, audio in enumerate(plan.audio):
        session.add(
            TimelineItem(
                version_id=version.id,
                asset_id=audio.asset_id,
                track=-(index + 1),
                start_frame=audio.timeline_start_frame,
                duration_frames=audio.duration_frames,
            )
        )
    await session.flush()
    return version


async def get_version(
    session: AsyncSession, project_id: UUID, owner_id: UUID, version_id: UUID
) -> EditVersion:
    await require_project(session, project_id, owner_id)
    version = await session.scalar(
        select(EditVersion).where(
            EditVersion.id == version_id, EditVersion.project_id == project_id
        )
    )
    if version is None:
        raise DomainError("version_not_found", "Edit version not found", 404)
    return version
