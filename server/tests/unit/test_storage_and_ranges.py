from pathlib import Path
from uuid import uuid4

import pytest
from fastapi import HTTPException, Request

from app.common.utils.file_download import ranged_file_response
from app.core.exceptions import DomainError
from app.integrations.storage_client import LocalStorage


def test_storage_rejects_traversal(tmp_path: Path):
    store = LocalStorage(tmp_path)
    with pytest.raises(DomainError):
        store.resolve("../private")


def test_storage_uses_logical_key_and_root(tmp_path: Path):
    store = LocalStorage(tmp_path)
    key = f"source/{uuid4().hex}.mp4"
    assert store.resolve(key).is_relative_to(tmp_path.resolve())


@pytest.mark.asyncio
async def test_range_download_returns_requested_byte_span(tmp_path: Path):
    path = tmp_path / "video.mp4"
    path.write_bytes(b"0123456789")
    scope = {"type": "http", "headers": [(b"range", b"bytes=2-5")], "method": "GET"}
    response = ranged_file_response(path, Request(scope), "video/mp4", "video.mp4")
    assert response.status_code == 206
    assert response.headers["content-range"] == "bytes 2-5/10"
    assert b"".join([chunk async for chunk in response.body_iterator]) == b"2345"


def test_invalid_range_is_rejected(tmp_path: Path):
    path = tmp_path / "video.mp4"
    path.write_bytes(b"123")
    scope = {"type": "http", "headers": [(b"range", b"bytes=10-20")], "method": "GET"}
    with pytest.raises(HTTPException) as error:
        ranged_file_response(path, Request(scope), "video/mp4", "video.mp4")
    assert error.value.status_code == 416
