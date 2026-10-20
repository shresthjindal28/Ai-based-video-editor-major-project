from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/integration")
async def integration_contract():
    return {
        "scheme": "Bearer JWT verified against AUTH_JWKS_URL",
        "required_claims": ["iss", "aud", "exp", "iat", "sub"],
        "required_settings": ["AUTH_ISSUER", "AUTH_AUDIENCE", "AUTH_JWKS_URL"],
        "accepted_algorithms": ["EdDSA", "RS256", "ES256"],
        "better_auth": "Configure the Better Auth JWT plugin with a published JWKS endpoint and issue API access tokens with the configured issuer and audience.",
    }
