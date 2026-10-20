from app.main import app
from app.modules.auth.service import IdentityVerifier
from app.modules.jobs.service import ACTIVE, TERMINAL


def test_core_routes_are_registered():
    paths = set(app.openapi()["paths"])
    assert "/health" in paths
    assert "/health/ready" in paths
    assert "/api/v1/projects/{project_id}/assets" in paths
    assert "/api/v1/projects/{project_id}/edits/{version_id}/render" in paths
    assert "/api/v1/jobs/{job_id}/events" in paths


def test_job_lifecycle_sets_are_disjoint():
    assert set(ACTIVE).isdisjoint(TERMINAL)


def test_auth_is_fail_closed_when_not_configured():
    verifier = IdentityVerifier()
    assert verifier.client is None
