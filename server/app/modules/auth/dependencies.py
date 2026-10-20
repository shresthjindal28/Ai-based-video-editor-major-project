from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DomainError
from app.db.session import get_session
from app.modules.auth.service import IdentityVerifier, synchronize
from app.modules.users.models import User

bearer = HTTPBearer(auto_error=False)
verifier = IdentityVerifier()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    if credentials is None or len(credentials.credentials) > 16384:
        raise DomainError("credentials_required", "Bearer token required", 401)
    return await synchronize(session, await verifier.verify(credentials.credentials))


CurrentUser = Annotated[User, Depends(get_current_user)]
DB = Annotated[AsyncSession, Depends(get_session)]
