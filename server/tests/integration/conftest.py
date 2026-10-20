"""Real-service tests create and remove only a private, randomly named schema."""
import os
import sys
from types import SimpleNamespace
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

import app.workers.tasks  # noqa: F401
from alembic import command
from app.core.config import get_settings
from app.db.session import get_session
from app.integrations.redis_client import close_redis
from app.integrations.storage_client import LocalStorage
from app.main import app
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User


@pytest_asyncio.fixture(loop_scope="module", scope="module")
async def backend(tmp_path_factory):
    if os.getenv("AUTOCUT_RUN_INTEGRATION") != "1":
        pytest.skip("Set AUTOCUT_RUN_INTEGRATION=1 for real PostgreSQL/Redis tests in an isolated schema")
    settings = get_settings()
    schema = f"autocut_test_{uuid4().hex}"
    admin = create_async_engine(settings.database_url, poolclass=NullPool)
    async with admin.begin() as connection:
        await connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = create_async_engine(settings.database_url, pool_size=5, max_overflow=5,
        connect_args={"server_settings": {"search_path": schema}})
    factory = async_sessionmaker(engine, expire_on_commit=False)
    patch = pytest.MonkeyPatch()
    media_root = tmp_path_factory.mktemp("autocut-media")
    local = LocalStorage(media_root)
    try:
        async with engine.begin() as connection:
            def migrate(sync_connection):
                cfg = Config("alembic.ini")
                cfg.attributes["connection"] = sync_connection
                command.upgrade(cfg, "head")
            await connection.run_sync(migrate)
        # Patch resource factories rather than database calls: repositories,
        # transactions, SQL, files, FFmpeg, MLT and Redis remain real.
        original_factory = sys.modules["app.db.session"].Session
        for name, module in list(sys.modules.items()):
            if name.startswith("app.") and module:
                if getattr(module, "Session", None) is original_factory:
                    patch.setattr(module, "Session", factory)
                if isinstance(getattr(module, "storage", None), LocalStorage):
                    patch.setattr(module, "storage", local)
        async def sessions():
            async with factory() as session:
                try:
                    yield session
                    await session.commit()
                except BaseException:
                    await session.rollback()
                    raise
        users = [User(external_subject=f"test:{uuid4().hex}", display_name="Test user") for _ in range(2)]
        async with factory() as session:
            session.add_all(users)
            await session.commit()
        identity = {"user": users[0]}
        async def test_identity():
            return identity["user"]
        app.dependency_overrides[get_session] = sessions
        app.dependency_overrides[get_current_user] = test_identity
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            yield SimpleNamespace(client=client, factory=factory, engine=engine, schema=schema,
                                  users=users, identity=identity, storage=local, root=media_root)
    finally:
        app.dependency_overrides.clear()
        patch.undo()
        await close_redis()
        await engine.dispose()
        async with admin.begin() as connection:
            await connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        await admin.dispose()
