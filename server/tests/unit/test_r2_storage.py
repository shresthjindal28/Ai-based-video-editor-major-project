from pathlib import Path

import pytest

import app.integrations.storage_client as module
from app.core.config import Settings
from app.core.exceptions import DomainError
from app.integrations.storage_client import R2Storage


@pytest.mark.asyncio
async def test_r2_fails_closed_without_credentials(tmp_path,monkeypatch):
    monkeypatch.setattr(module,"get_settings",lambda:Settings(_env_file=None,r2_endpoint_url="",r2_bucket="",r2_access_key_id="",r2_secret_access_key=""))
    backend=R2Storage(tmp_path)
    backend.path("test.bin").write_bytes(b"test")
    with pytest.raises(DomainError) as error:
        await backend.publish("test.bin")
    assert error.value.code == "storage_unconfigured"


@pytest.mark.asyncio
async def test_r2_roundtrip_uses_sdk_transfers_and_safe_staging(tmp_path,monkeypatch):
    objects={}
    class Client:
        def upload_file(self,path,bucket,key,**kwargs):
            objects[key]=Path(path).read_bytes()
        def head_object(self,**kwargs):
            return {"ContentLength":len(objects[kwargs["Key"]])}
        def download_file(self,bucket,key,path):
            Path(path).write_bytes(objects[key])
        def delete_object(self,**kwargs):
            objects.pop(kwargs["Key"],None)
        def close(self):
            return None
    backend=R2Storage(tmp_path)
    monkeypatch.setattr(backend,"_client",lambda:Client())
    key="source/example.dat"
    path=backend.path(key)
    path.parent.mkdir(parents=True)
    path.write_bytes(b"object-store fixture")
    await backend.publish(key)
    backend.delete(key)
    assert (await backend.materialize(key)).read_bytes()==b"object-store fixture"
    await backend.remove(key)
    assert not objects and not path.exists()
