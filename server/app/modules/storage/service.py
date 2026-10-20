"""Durable object reservations close database/object-store failure windows."""
from datetime import timedelta

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.base import now
from app.db.session import Session
from app.integrations.storage_client import storage
from app.modules.storage.models import FileDeletion


async def reserve(key: str) -> None:
    # Commit before creating/publishing a file. If the worker dies, cleanup
    # eventually removes only this attempt's private, unreferenced key.
    storage.path(key)
    async with Session() as session:
        await session.execute(insert(FileDeletion).values(storage_key=key,
            available_at=now()+timedelta(seconds=get_settings().upload_session_ttl_seconds)).on_conflict_do_nothing())
        await session.commit()


async def keep(session: AsyncSession, keys: list[str]) -> None:
    await session.execute(delete(FileDeletion).where(FileDeletion.storage_key.in_(keys)))


async def cleanup() -> int:
    count = 0
    async with Session() as session:
        from app.modules.uploads.sessions import expire
        await expire(session)
        rows = list((await session.scalars(select(FileDeletion).where(FileDeletion.available_at <= now())
                     .order_by(FileDeletion.available_at).limit(20).with_for_update(skip_locked=True))).all())
        for row in rows:
            try:
                await storage.remove(row.storage_key)
            except Exception as exc:
                row.attempts += 1
                row.last_error = type(exc).__name__
                row.available_at = now()+timedelta(seconds=min(3600, 2**min(row.attempts, 12)))
            else:
                await session.delete(row)
                count += 1
        await session.commit()
    return count
