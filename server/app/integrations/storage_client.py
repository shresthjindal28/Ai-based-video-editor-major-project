from __future__ import annotations

import hashlib
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
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


storage = LocalStorage()
