import hashlib
import json
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DomainError
from app.modules.auth.models import IdempotencyRecord


async def begin(
    session: AsyncSession, user: UUID, scope: str, key: str | None, payload: object
) -> IdempotencyRecord | None:
    if key is None:
        return None
    if not 1 <= len(key) <= 200:
        raise DomainError("invalid_idempotency_key", "Key must be 1–200 characters")
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()
    await session.execute(
        insert(IdempotencyRecord)
        .values(user_id=user, scope=scope, key=key, fingerprint=digest)
        .on_conflict_do_nothing()
    )
    row = (
        await session.scalars(
            select(IdempotencyRecord)
            .where(
                IdempotencyRecord.user_id == user,
                IdempotencyRecord.scope == scope,
                IdempotencyRecord.key == key,
            )
            .with_for_update()
        )
    ).one()
    if row.fingerprint != digest:
        raise DomainError("idempotency_conflict", "Key was used with a different request", 409)
    return row


def finish(record: IdempotencyRecord | None, result: dict) -> None:
    if record:
        record.status, record.result = "completed", result
