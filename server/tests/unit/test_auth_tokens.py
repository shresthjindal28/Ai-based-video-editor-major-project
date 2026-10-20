from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

import app.modules.auth.service as service
from app.core.config import Settings
from app.core.exceptions import DomainError


@pytest.fixture
def identity(monkeypatch):
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    settings = Settings(_env_file=None, auth_issuer="https://identity.test", auth_audience="autocut",
                        auth_jwks_url="https://identity.test/jwks", auth_algorithms=["RS256"])
    monkeypatch.setattr(service, "get_settings", lambda: settings)
    verifier = service.IdentityVerifier()
    verifier.client = SimpleNamespace(get_signing_key_from_jwt=lambda token: SimpleNamespace(key=private.public_key()))
    claims = {"iss": settings.auth_issuer, "aud": settings.auth_audience, "sub": "test-user",
              "iat": datetime.now(UTC), "exp": datetime.now(UTC)+timedelta(minutes=5)}
    return verifier, private, claims


@pytest.mark.asyncio
async def test_verifies_real_signature(identity):
    verifier, key, claims = identity
    token = jwt.encode(claims, key, algorithm="RS256")
    assert (await verifier.verify(token))["sub"] == "test-user"


@pytest.mark.parametrize("mutation", ["issuer", "audience", "expired", "signature", "missing_subject"])
@pytest.mark.asyncio
async def test_rejects_bad_signature_and_claims(identity, mutation):
    verifier, key, claims = identity
    if mutation == "issuer":
        claims["iss"] = "https://untrusted.test"
    elif mutation == "audience":
        claims["aud"] = "another-api"
    elif mutation == "expired":
        claims["exp"] = datetime.now(UTC)-timedelta(minutes=1)
    elif mutation == "signature":
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    else:
        del claims["sub"]
    with pytest.raises(DomainError) as error:
        await verifier.verify(jwt.encode(claims,key,algorithm="RS256"))
    assert error.value.status == 401


@pytest.mark.asyncio
async def test_missing_configuration_fails_closed(monkeypatch):
    monkeypatch.setattr(service,"get_settings",lambda:Settings(_env_file=None,auth_jwks_url="",auth_issuer="",auth_audience=""))
    with pytest.raises(DomainError) as error:
        await service.IdentityVerifier().verify("untrusted")
    assert error.value.code == "auth_unconfigured"
