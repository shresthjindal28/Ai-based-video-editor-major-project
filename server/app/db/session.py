import asyncio
import random
import time
from collections.abc import AsyncIterator, Awaitable, Callable

from sqlalchemy import event
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.metrics import DB_TIME

s = get_settings()
engine = create_async_engine(
    s.database_url,
    pool_size=s.db_pool_size,
    max_overflow=s.db_max_overflow,
    pool_pre_ping=True,
    pool_recycle=s.db_pool_recycle,
    isolation_level="READ COMMITTED",
    connect_args={"server_settings": {"application_name": "autocut-main"}},
)
Session = async_sessionmaker(engine, expire_on_commit=False)


@event.listens_for(engine.sync_engine, "before_cursor_execute")
def before(conn, cursor, statement, parameters, context, executemany):
    context.query_started = time.monotonic()


@event.listens_for(engine.sync_engine, "after_cursor_execute")
def after(conn, cursor, statement, parameters, context, executemany):
    DB_TIME.observe(time.monotonic() - context.query_started)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with Session() as session:
        try:
            yield session
            await session.commit()
        except BaseException:
            await session.rollback()
            raise


async def dispose_engine() -> None:
    await engine.dispose()


async def transaction_retry[T](operation: Callable[[], Awaitable[T]], attempts: int = 3) -> T:
    """Operation must open a fresh transaction each attempt; never repeat external effects."""
    for attempt in range(attempts):
        try:
            return await operation()
        except DBAPIError as exc:
            code = getattr(exc.orig, "sqlstate", None)
            if code not in {"40001", "40P01"} or attempt == attempts - 1:
                raise
            await asyncio.sleep(random.uniform(0.01, 0.1) * 2**attempt)
    raise RuntimeError("unreachable")
