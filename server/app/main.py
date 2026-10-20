from __future__ import annotations

import logging
import shutil
import time
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import text
from starlette.exceptions import HTTPException

from app.common.middleware.body_size import RequestSizeMiddleware
from app.core.config import get_settings
from app.core.exceptions import DomainError
from app.core.logging import configure_logging, request_id
from app.core.metrics import REQUESTS
from app.db.session import Session, dispose_engine
from app.integrations.redis_client import close_redis, redis_client
from app.modules.analytics.router import router as analytics_router
from app.modules.assets.router import router as assets_router
from app.modules.audio.router import router as audio_router
from app.modules.auth.router import router as auth_router
from app.modules.billing.router import router as billing_router
from app.modules.editor.router import router as editor_router
from app.modules.effects.router import router as effects_router
from app.modules.exports.router import router as exports_router
from app.modules.jobs.router import router as jobs_router
from app.modules.notifications.router import router as notifications_router
from app.modules.projects.router import router as projects_router
from app.modules.rendering.router import router as rendering_router
from app.modules.subscriptions.router import router as subscriptions_router
from app.modules.timelines.router import router as timelines_router
from app.modules.transitions.router import router as transitions_router
from app.modules.uploads.router import router as uploads_router
from app.modules.users.router import router as users_router

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging(settings.log_level)
    settings.media_storage_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    yield
    await close_redis()
    await dispose_engine()


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.app_name, version="1.0.0", debug=settings.debug, lifespan=lifespan
    )
    application.add_middleware(RequestSizeMiddleware, settings=settings)
    if settings.cors_origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PATCH", "DELETE", "HEAD", "OPTIONS"],
            allow_headers=[
                "Authorization",
                "Content-Type",
                "Idempotency-Key",
                "Last-Event-ID",
                "Range",
                "Upload-Offset",
            ],
            expose_headers=["Content-Range", "Accept-Ranges", "Content-Length", "X-Request-ID"],
        )

    @application.middleware("http")
    async def request_context(request: Request, call_next):
        incoming = request.headers.get("X-Request-ID", "")
        correlation_id = (
            incoming if 0 < len(incoming) <= 128 and incoming.isprintable() else str(uuid4())
        )
        token = request_id.set(correlation_id)
        started = time.monotonic()
        if request.headers.get("content-length", "").isdigit():
            route_limit = (
                settings.max_upload_size_mb * 1024 * 1024 + 1024 * 1024
                if "/assets" in request.url.path
                else settings.request_max_bytes
            )
            if request.url.path.endswith("/chunks"):
                route_limit = settings.upload_chunk_size_bytes
            if int(request.headers["content-length"]) > route_limit:
                request_id.reset(token)
                return JSONResponse(
                    {
                        "error": {
                            "code": "request_too_large",
                            "message": "Request exceeds the configured size limit",
                        }
                    },
                    status_code=413,
                )
        try:
            response = await call_next(request)
        finally:
            # Record metrics/log context before clearing the request-local correlation ID.
            if "response" in locals():
                response.headers["X-Request-ID"] = correlation_id
                REQUESTS.labels(method=request.method, status=str(response.status_code)).observe(
                    time.monotonic() - started
                )
                logger.info(
                    "request completed",
                    extra={
                        "operation": request.url.path,
                        "duration": time.monotonic() - started,
                        "outcome": response.status_code,
                    },
                )
            request_id.reset(token)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["X-Frame-Options"] = "DENY"
        if settings.app_env == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    @application.exception_handler(DomainError)
    async def domain_error_handler(_: Request, exc: DomainError):
        body: dict[str, dict[str, object]] = {"error": {"code": exc.code, "message": exc.message}}
        if exc.details is not None and settings.debug:
            body["error"]["details"] = exc.details
        return JSONResponse(body, status_code=exc.status)

    @application.exception_handler(Exception)
    async def unhandled_error_handler(_: Request, exc: Exception):
        logger.exception("unhandled request error", extra={"error_code": "internal_error"})
        return JSONResponse(
            {"error": {"code": "internal_error", "message": "Internal server error"}},
            status_code=500,
        )

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(_: Request, exc: RequestValidationError):
        return JSONResponse({"error": {"code": "validation_error", "message": "Request validation failed",
            "details": [{"location": list(error["loc"]), "message": error["msg"], "type": error["type"]}
                        for error in exc.errors()]}}, status_code=422)

    @application.exception_handler(HTTPException)
    async def http_error_handler(_: Request, exc: HTTPException):
        codes = {401: "credentials_required", 404: "not_found", 413: "request_too_large"}
        return JSONResponse({"error": {"code": codes.get(exc.status_code, "http_error"),
                                       "message": str(exc.detail)}}, status_code=exc.status_code,
                            headers=exc.headers)

    @application.get("/health")
    async def health():
        return {"status": "ok", "service": "main-backend"}

    @application.get("/health/ready")
    async def readiness():
        checks: dict[str, str] = {}
        try:
            async with Session() as session:
                await session.execute(text("SELECT 1"))
            checks["postgres"] = "ok"
        except Exception:
            checks["postgres"] = "unavailable"
        try:
            await redis_client().ping()
            checks["redis"] = "ok"
        except Exception:
            checks["redis"] = "unavailable"
        for name, binary in (("ffmpeg", settings.ffmpeg_binary), ("ffprobe", settings.ffprobe_binary),
                             ("mlt", settings.mlt_render_binary)):
            checks[name] = "ok" if shutil.which(binary) else "unavailable"
        checks["authentication"] = "ok" if all((settings.auth_jwks_url, settings.auth_issuer, settings.auth_audience)) else "unconfigured"
        checks["storage"] = "ok"
        if settings.storage_backend == "r2" and not all((settings.r2_endpoint_url, settings.r2_bucket,
                                                        settings.r2_access_key_id, settings.r2_secret_access_key)):
            checks["storage"] = "unconfigured"
        status = 200 if all(value == "ok" for value in checks.values()) else 503
        return JSONResponse(
            {"status": "ready" if status == 200 else "not_ready", "checks": checks},
            status_code=status,
        )

    @application.get("/metrics", include_in_schema=False)
    async def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    routers = (
        auth_router,
        users_router,
        projects_router,
        uploads_router,
        assets_router,
        editor_router,
        timelines_router,
        audio_router,
        effects_router,
        transitions_router,
        jobs_router,
        rendering_router,
        exports_router,
        notifications_router,
        analytics_router,
        billing_router,
        subscriptions_router,
    )
    for route in routers:
        application.include_router(route, prefix=settings.api_prefix)
    return application


app = create_app()
