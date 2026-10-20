
import pytest

from app.integrations.redis_client import Cache


class UnavailableRedis:
    async def get(self,*args,**kwargs):
        raise ConnectionError("redis unavailable")
    async def set(self,*args,**kwargs):
        raise ConnectionError("redis unavailable")
    async def delete(self,*args,**kwargs):
        raise ConnectionError("redis unavailable")


@pytest.mark.asyncio
async def test_cache_failure_uses_authoritative_loader():
    calls=0
    async def loader():
        nonlocal calls
        calls += 1
        return {"source":"database"}
    cache=Cache(client=UnavailableRedis())
    assert await cache.get_or_load("user:summary",loader)=={"source":"database"}
    await cache.invalidate("user:summary")
    assert calls == 1
