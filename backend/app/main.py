"""FastAPI uygulama fabrikası — tüm middleware, router ve event handler'ları burada bağlanır."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.health import health_router
from app.api.router import api_router
from app.config import get_settings
from app.core.redis_client import redis_manager
from app.database import engine
from app.exceptions import register_exception_handlers
from app.logging_config import setup_logging
from app.middleware import RateLimitMiddleware, RequestLoggingMiddleware

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama başlatma ve kapatma olayları."""
    # ── Startup ──
    setup_logging(settings.LOG_LEVEL)
    await redis_manager.connect()

    # Sentry entegrasyonu
    if settings.SENTRY_DSN:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration

        sentry_sdk.init(dsn=settings.SENTRY_DSN, integrations=[FastApiIntegration()])

    yield

    # ── Shutdown ──
    await redis_manager.disconnect()
    await engine.dispose()


def create_app() -> FastAPI:
    """FastAPI uygulamasını oluştur ve yapılandır."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="BIST İçin AI Destekli Otomatik Ticaret Platformu",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # ── Exception Handler'lar ──
    register_exception_handlers(app)

    # ── Middleware (sıra önemli: ilk eklenen en dışta çalışır) ──
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    if settings.ENVIRONMENT == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*.bist-robogo.com", "localhost"],
        )

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)

    # ── Router'lar ──
    app.include_router(health_router, tags=["health"])
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


# Uvicorn bu nesneyi kullanır: uvicorn app.main:app
app = create_app()
