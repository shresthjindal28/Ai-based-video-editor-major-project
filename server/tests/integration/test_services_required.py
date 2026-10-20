import os
import shutil

import pytest

pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    not os.getenv("TEST_DATABASE_URL"),
    reason="Set TEST_DATABASE_URL to run PostgreSQL integration workflow",
)
def test_postgres_service_is_configured():
    assert os.environ["TEST_DATABASE_URL"].startswith("postgresql+asyncpg://")


@pytest.mark.mlt
@pytest.mark.skipif(
    shutil.which("melt") is None, reason="MLT melt executable is unavailable in this environment"
)
def test_mlt_engine_is_installed_for_render_integration():
    assert shutil.which("melt") is not None
