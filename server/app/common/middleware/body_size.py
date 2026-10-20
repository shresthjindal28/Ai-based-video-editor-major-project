from starlette.exceptions import HTTPException
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.config import Settings


class RequestSizeMiddleware:
    """Count actual ASGI bytes, including requests without Content-Length."""

    def __init__(self, app: ASGIApp, settings: Settings):
        self.app, self.settings = app, settings

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        path = scope["path"]
        limit = self.settings.request_max_bytes
        if "/assets" in path:
            limit = self.settings.max_upload_size_mb*1024**2 + 1024**2
        if path.endswith("/chunks"):
            limit = self.settings.upload_chunk_size_bytes
        received = 0

        async def bounded_receive():
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > limit:
                    raise HTTPException(413, "Request exceeds the configured size limit")
            return message

        await self.app(scope, bounded_receive, send)
