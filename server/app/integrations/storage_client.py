from __future__ import annotations

import hashlib
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol
from uuid import uuid4

import anyio
from fastapi import UploadFile

from app.core.config import get_settings
from app.core.exceptions import DomainError

_SAFE_KEY = re.compile(r"^[a-zA-Z0-9._/-]+$")


@dataclass(frozen=True)
class StoredFile:
    key: str
    path: Path
    size: int
    checksum: str


class StorageBackend(Protocol):
    async def publish(self, key: str) -> None: ...
    async def materialize(self, key: str) -> Path: ...
    async def remove(self, key: str) -> None: ...
    def path(self, key: str) -> Path: ...


class LocalStorage:
    """Private local storage. Keys are logical identifiers, never client paths."""

    def __init__(self, root: Path | None = None):
        self.root = (root or get_settings().media_storage_root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)

    def resolve(self, key: str) -> Path:
        if not _SAFE_KEY.fullmatch(key) or key.startswith("/") or ".." in key.split("/"):
            raise DomainError("invalid_storage_key", "Invalid storage key", 400)
        path = (self.root / key).resolve()
        if not path.is_relative_to(self.root):
            raise DomainError("invalid_storage_key", "Invalid storage key", 400)
        return path

    async def save_upload(
        self, upload: UploadFile, *, max_bytes: int, suffix: str = ""
    ) -> StoredFile:
        key = f"source/{uuid4().hex}{suffix[:16]}"
        destination = self.resolve(key)
        destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd, temp_name = tempfile.mkstemp(prefix=".upload-", dir=destination.parent)
        os.close(fd)
        size, digest = 0, hashlib.sha256()
        try:
            async with await anyio.open_file(temp_name, "wb") as output:
                while chunk := await upload.read(1024 * 1024):
                    size += len(chunk)
                    if size > max_bytes:
                        raise DomainError(
                            "upload_too_large", "Upload exceeds the configured size limit", 413
                        )
                    digest.update(chunk)
                    await output.write(chunk)
                await output.flush()
            if size == 0:
                raise DomainError("empty_upload", "Uploaded file is empty", 400)
            os.replace(temp_name, destination)
            return StoredFile(key, destination, size, digest.hexdigest())
        except BaseException:
            Path(temp_name).unlink(missing_ok=True)
            raise

    def exists(self, key: str) -> bool:
        return self.resolve(key).is_file()

    def delete(self, key: str) -> None:
        self.resolve(key).unlink(missing_ok=True)

    def delete_if_unreferenced(self, key: str) -> None:
        self.delete(key)

    def path(self, key: str) -> Path:
        return self.resolve(key)

    async def publish(self, key: str) -> None:
        if not self.path(key).is_file():
            raise DomainError("storage_missing", "Media file is unavailable", 410)

    async def materialize(self, key: str) -> Path:
        path = self.path(key)
        if not path.is_file():
            raise DomainError("storage_missing", "Media file is unavailable", 410)
        return path

    async def remove(self, key: str) -> None:
        self.delete(key)


class R2Storage(LocalStorage):
    """R2 is durable storage; the private local directory is a render workspace.

    SDK networking and multipart transfers run in AnyIO's bounded thread pool.
    No bucket URL or client-supplied storage key is exposed publicly.
    """

    def _client(self) -> Any:
        import boto3
        from botocore.config import Config

        settings = get_settings()
        if not all((settings.r2_endpoint_url, settings.r2_bucket,
                    settings.r2_access_key_id, settings.r2_secret_access_key)):
            raise DomainError("storage_unconfigured", "R2 storage credentials are not configured", 503)
        if not settings.r2_endpoint_url.startswith("https://"):
            raise DomainError("storage_unconfigured", "R2 requires an HTTPS endpoint", 503)
        return boto3.client(
            "s3", endpoint_url=settings.r2_endpoint_url,
            aws_access_key_id=settings.r2_access_key_id,
            aws_secret_access_key=settings.r2_secret_access_key,
            region_name="auto",
            config=Config(connect_timeout=10, read_timeout=60,
                          request_checksum_calculation="when_required", response_checksum_validation="when_required",
                          retries={"max_attempts": 3, "mode": "standard"}),
        )

    async def publish(self, key: str) -> None:
        path = await super().materialize(key)

        def transfer() -> None:
            from boto3.s3.transfer import TransferConfig

            client = self._client()
            try:
                client.upload_file(str(path), get_settings().r2_bucket, key,
                    Config=TransferConfig(max_concurrency=2, multipart_threshold=8 * 1024**2))
                metadata = client.head_object(Bucket=get_settings().r2_bucket, Key=key)
                if metadata["ContentLength"] != path.stat().st_size:
                    raise DomainError("storage_verification_failed", "Stored object size differs from upload", 503)
            finally:
                client.close()

        await anyio.to_thread.run_sync(transfer)

    async def materialize(self, key: str) -> Path:
        path = self.path(key)
        if path.is_file():
            return path

        def transfer() -> None:
            from botocore.exceptions import ClientError

            path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            fd, temp_name = tempfile.mkstemp(prefix=".download-", dir=path.parent)
            os.close(fd)
            client = self._client()
            try:
                client.download_file(get_settings().r2_bucket, key, temp_name)
                os.replace(temp_name, path)
            except ClientError as exc:
                if str(exc.response.get("Error", {}).get("Code")) in {"404", "NoSuchKey"}:
                    raise DomainError("storage_missing", "Media file is unavailable", 410) from exc
                raise
            finally:
                Path(temp_name).unlink(missing_ok=True)
                client.close()

        await anyio.to_thread.run_sync(transfer)
        return path

    async def remove(self, key: str) -> None:
        self.resolve(key)

        def remove_remote() -> None:
            client = self._client()
            try:
                client.delete_object(Bucket=get_settings().r2_bucket, Key=key)
            finally:
                client.close()

        await anyio.to_thread.run_sync(remove_remote)
        self.delete(key)


storage = R2Storage() if get_settings().storage_backend == "r2" else LocalStorage()
