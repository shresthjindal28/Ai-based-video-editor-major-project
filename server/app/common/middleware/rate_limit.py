from uuid import UUID

from app.core.config import get_settings
from app.core.exceptions import DomainError
from app.integrations.redis_client import redis_client


async def check_expensive_operation(scope: str, identity: UUID) -> None:
    client = redis_client()
    key = f"autocut:rate:v1:{scope}:{identity}"
    try:
        count = await client.eval(
            "local n=redis.call('INCR',KEYS[1]); if n==1 then redis.call('EXPIRE',KEYS[1],60) end; return n",
            1,
            key,
        )
    except Exception as exc:
        raise DomainError(
            "rate_limit_unavailable", "Expensive operation capacity is temporarily unavailable", 503
        ) from exc
    if int(count) > get_settings().expensive_requests_per_minute:
        raise DomainError("rate_limited", "Too many expensive requests; retry shortly", 429)
