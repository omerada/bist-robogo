# Source: Doc 07 §6 — Middleware
"""Özel middleware tanımları.

NOT: BaseHTTPMiddleware kullanmıyoruz çünkü call_next() içinde ayrı bir
anyio task spawn eder. Bu, pytest + ASGITransport ortamında asyncpg
bağlantısının "got Future attached to a different loop" hatasına yol açar.
Bunun yerine saf ASGI middleware kullanıyoruz.
"""

import time
import uuid

import structlog
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.rate_limiter import check_rate_limit

logger = structlog.get_logger()


class RequestLoggingMiddleware:
    """Her HTTP isteğini loglar, request ID ekler ve süresini ölçer.

    Pure ASGI middleware — BaseHTTPMiddleware'in task-spawn sorununu önler.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http",):
            await self.app(scope, receive, send)
            return

        request_id = str(uuid.uuid4())[:8]
        # scope["state"] üzerinden request.state'e atama
        scope.setdefault("state", {})
        scope["state"]["request_id"] = request_id

        start_time = time.perf_counter()

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=scope["method"],
            path=scope["path"],
        )

        logger.info("request_started")

        status_code = 500  # default, will be overwritten by response

        async def send_with_headers(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                headers = dict(message.get("headers", []))
                duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
                extra_headers = [
                    (b"x-request-id", request_id.encode()),
                    (b"x-response-time", f"{duration_ms}ms".encode()),
                ]
                message["headers"] = list(message.get("headers", [])) + extra_headers

                logger.info(
                    "request_completed",
                    status_code=status_code,
                    duration_ms=duration_ms,
                )
            await send(message)

        await self.app(scope, receive, send_with_headers)


class RateLimitMiddleware:
    """Redis tabanlı rate limiting. Her IP adresi dakikada 60 istek yapabilir.

    Pure ASGI middleware — BaseHTTPMiddleware'in task-spawn sorununu önler.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http",):
            await self.app(scope, receive, send)
            return

        path = scope["path"]
        # Health endpoint'leri ve docs rate limit dışı
        if path in ("/health", "/ready", "/docs", "/openapi.json"):
            await self.app(scope, receive, send)
            return

        # Client IP'yi scope'tan al
        client = scope.get("client")
        client_ip = client[0] if client else "unknown"
        is_allowed = await check_rate_limit(client_ip, max_requests=60, window_seconds=60)

        if not is_allowed:
            response = JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": {
                        "code": "RATE_LIMITED",
                        "message": "Çok fazla istek gönderildi. Lütfen bekleyin.",
                    },
                },
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)
