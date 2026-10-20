from collections.abc import Iterator
from pathlib import Path

from fastapi import HTTPException, Request
from fastapi.responses import StreamingResponse


def ranged_file_response(
    path: Path, request: Request, media_type: str, filename: str
) -> StreamingResponse:
    size = path.stat().st_size
    header = request.headers.get("range")
    start, end, status = 0, size - 1, 200
    headers = {
        "Accept-Ranges": "bytes",
        "Content-Length": str(size),
        "Content-Disposition": f'attachment; filename="{filename.replace(chr(34), "")}"',
    }
    if header:
        if not header.startswith("bytes=") or "," in header:
            raise HTTPException(
                status_code=416,
                detail="A single byte range is supported",
                headers={"Content-Range": f"bytes */{size}"},
            )
        value = header[6:]
        first, separator, last = value.partition("-")
        if not separator:
            raise HTTPException(status_code=416, headers={"Content-Range": f"bytes */{size}"})
        try:
            if first:
                start, end = int(first), int(last) if last else size - 1
            else:
                suffix = int(last)
                start, end = max(0, size - suffix), size - 1
        except ValueError as exc:
            raise HTTPException(
                status_code=416, headers={"Content-Range": f"bytes */{size}"}
            ) from exc
        if start < 0 or end < start or start >= size:
            raise HTTPException(status_code=416, headers={"Content-Range": f"bytes */{size}"})
        end = min(end, size - 1)
        status = 206
        headers["Content-Length"] = str(end - start + 1)
        headers["Content-Range"] = f"bytes {start}-{end}/{size}"

    def body() -> Iterator[bytes]:
        with path.open("rb") as source:
            source.seek(start)
            remaining = end - start + 1
            while remaining:
                chunk = source.read(min(1024 * 1024, remaining))
                if not chunk:
                    break
                remaining -= len(chunk)
                yield chunk

    return StreamingResponse(body(), status_code=status, media_type=media_type, headers=headers)
