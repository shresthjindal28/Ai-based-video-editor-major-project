import asyncio

import jwt
from jwt.jwks_client import PyJWKClient
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import DomainError
from app.modules.users.models import User


class IdentityVerifier:
    def __init__(self) -> None:
        s = get_settings()
        self.settings = s
        self.client = (
            PyJWKClient(s.auth_jwks_url, cache_jwk_set=True, lifespan=300, timeout=5)
            if s.auth_jwks_url
            else None
        )

    async def verify(self, token: str) -> dict:
        s = self.settings
        if not self.client or not s.auth_issuer or not s.auth_audience:
            raise DomainError("auth_unconfigured", "Identity verification is not configured", 503)
        try:
            key = await asyncio.to_thread(self.client.get_signing_key_from_jwt, token)
            claims = jwt.decode(
                token,
                key.key,
                algorithms=s.auth_algorithms,
                issuer=s.auth_issuer,
                audience=s.auth_audience,
                options={"require": ["exp", "iat", "iss", "aud", "sub"]},
                leeway=5,
            )
            if not isinstance(claims["sub"], str) or not 1 <= len(claims["sub"]) <= 255:
                raise ValueError("invalid subject")
            return claims
        except (jwt.PyJWTError, ValueError) as exc:
            raise DomainError(
                "invalid_credentials", "Invalid or expired bearer token", 401
            ) from exc


async def synchronize(session: AsyncSession, claims: dict) -> User:
    subject = claims["sub"]
    values = {
        "external_subject": subject,
        "email": claims.get("email"),
        "display_name": claims.get("name"),
    }
    await session.execute(
        insert(User).values(**values).on_conflict_do_nothing(index_elements=[User.external_subject])
    )
    user = (await session.scalars(select(User).where(User.external_subject == subject))).one()
    if user.status != "active":
        raise DomainError("user_disabled", "Account is unavailable", 403)
    user.email, user.display_name = values["email"], values["display_name"]
    return user
