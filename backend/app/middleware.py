# Source: Doc 07 §6 — Middleware
"""Özel middleware tanımları."""

import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.rate_limiter import check_rate_limit

logger = structlog.get_logger()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Her HTTP isteğini loglar, request ID ekler ve süresini ölçer."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        start_time = time.perf_counter()

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        logger.info("request_started")

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration_ms}ms"

        logger.info(
            "request_completed",
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Redis tabanlı rate limiting. Her IP adresi dakikada 60 istek yapabilir."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Health endpoint'leri ve docs rate limit dışı
        if request.url.path in ("/health", "/ready", "/docs", "/openapi.json"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        is_allowed = await check_rate_limit(client_ip, max_requests=60, window_seconds=60)

        if not is_allowed:
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": {
                        "code": "RATE_LIMITED",
                        "message": "Çok fazla istek gönderildi. Lütfen bekleyin.",
                    },
                },
            )

        return await call_next(request)
