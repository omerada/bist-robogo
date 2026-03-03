# bist-robogo — Backend Implementasyon Kılavuzu

> **Proje:** bist-robogo — BIST İçin AI Destekli Otomatik Ticaret Platformu  
> **Versiyon:** 1.0  
> **Tarih:** 2026-03-03  
> **Amaç:** AI Agent'ın backend sistemini sıfır hata ile geliştirebilmesi için dosya dosya, satır satır implementasyon rehberi.

---

## 1. Backend Dizin Yapısı (Tam)

```
backend/
├── pyproject.toml                    # Poetry paket yönetimi
├── poetry.lock                       # Kilit dosyası (otomatik üretilir)
├── alembic.ini                       # Alembic yapılandırma
├── Dockerfile                        # Backend Docker image
├── .env                              # Ortam değişkenleri (git'e eklenmez)
├── .env.example                      # Örnek ortam değişkenleri
│
├── alembic/                          # Veritabanı migration'ları
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial_schema.py
│
├── app/                              # Ana uygulama paketi
│   ├── __init__.py
│   ├── main.py                       # FastAPI uygulama fabrikası
│   ├── config.py                     # Pydantic Settings — ortam değişkenleri
│   ├── database.py                   # SQLAlchemy engine, session, Base
│   ├── dependencies.py               # FastAPI dependency injection
│   ├── exceptions.py                 # Custom exception sınıfları
│   ├── middleware.py                  # Middleware tanımları
│   ├── logging_config.py             # structlog yapılandırması
│   │
│   ├── models/                       # SQLAlchemy ORM modelleri
│   │   ├── __init__.py               # Tüm modelleri re-export
│   │   ├── base.py                   # BaseModel (timestamp mixin)
│   │   ├── user.py                   # User, ApiKey
│   │   ├── broker.py                 # BrokerConnection
│   │   ├── market.py                 # Symbol, Index, IndexComponent
│   │   ├── strategy.py               # Strategy, Signal
│   │   ├── order.py                  # Order, Trade
│   │   ├── portfolio.py              # Portfolio, Position, PortfolioSnapshot
│   │   ├── risk.py                   # RiskRule, RiskEvent
│   │   ├── backtest.py               # BacktestRun, BacktestTrade
│   │   ├── notification.py           # Notification
│   │   └── audit.py                  # AuditLog
│   │
│   ├── schemas/                      # Pydantic request/response şemaları
│   │   ├── __init__.py
│   │   ├── common.py                 # APIResponse, PaginationMeta, ErrorResponse
│   │   ├── auth.py                   # LoginRequest, RegisterRequest, TokenResponse
│   │   ├── user.py                   # UserResponse, UserUpdate
│   │   ├── market.py                 # QuoteResponse, OHLCVResponse, SymbolResponse
│   │   ├── order.py                  # OrderCreateRequest, OrderResponse
│   │   ├── portfolio.py              # PortfolioSummary, PositionResponse
│   │   ├── strategy.py               # StrategyCreate, StrategyResponse, SignalResponse
│   │   ├── backtest.py               # BacktestRequest, BacktestResultResponse
│   │   ├── risk.py                   # RiskStatusResponse, RiskRuleUpdate
│   │   ├── trend.py                  # TrendAnalysisRequest, TrendCandidateResponse
│   │   └── notification.py           # NotificationResponse
│   │
│   ├── api/                          # API router'ları (endpoint tanımları)
│   │   ├── __init__.py
│   │   ├── router.py                 # Ana router (tüm alt-router'ları birleştirir)
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py               # /api/v1/auth/*
│   │   │   ├── market.py             # /api/v1/market/*
│   │   │   ├── orders.py             # /api/v1/orders/*
│   │   │   ├── portfolio.py          # /api/v1/portfolio/*
│   │   │   ├── strategies.py         # /api/v1/strategies/*
│   │   │   ├── backtest.py           # /api/v1/backtest/*
│   │   │   ├── risk.py               # /api/v1/risk/*
│   │   │   ├── trends.py             # /api/v1/analysis/trends
│   │   │   ├── ml.py                 # /api/v1/ml/*
│   │   │   └── notifications.py      # /api/v1/notifications/*
│   │   └── health.py                 # /health, /ready
│   │
│   ├── services/                     # İş mantığı katmanı
│   │   ├── __init__.py
│   │   ├── auth_service.py           # Kayıt, giriş, token yönetimi, 2FA
│   │   ├── market_data_service.py    # Veri toplama, cache, dağıtım
│   │   ├── trading_service.py        # Emir oluşturma, validasyon, durum takibi
│   │   ├── portfolio_service.py      # Pozisyon, PnL, snapshot hesaplama
│   │   ├── strategy_service.py       # Strateji CRUD, sinyal üretimi
│   │   ├── backtest_service.py       # Backtest simülasyonu, metrik hesaplama
│   │   ├── risk_service.py           # Risk kontrol, limit yönetimi
│   │   ├── trend_analysis_service.py # Dip/kırılım tespiti
│   │   ├── notification_service.py   # Bildirim gönderme (in-app, email, telegram)
│   │   ├── ml_service.py             # Model inference, feature engineering
│   │   └── scheduler_service.py      # Zamanlı görev yönetimi
│   │
│   ├── repositories/                 # Veritabanı erişim katmanı
│   │   ├── __init__.py
│   │   ├── base.py                   # BaseRepository (generic CRUD)
│   │   ├── user_repo.py
│   │   ├── market_repo.py
│   │   ├── order_repo.py
│   │   ├── portfolio_repo.py
│   │   ├── strategy_repo.py
│   │   ├── backtest_repo.py
│   │   ├── risk_repo.py
│   │   └── notification_repo.py
│   │
│   ├── core/                         # Çekirdek yardımcı modüller
│   │   ├── __init__.py
│   │   ├── security.py               # JWT encode/decode, password hash/verify
│   │   ├── redis_client.py           # Redis bağlantı yönetimi
│   │   ├── kafka_client.py           # Kafka producer/consumer
│   │   ├── websocket_manager.py      # WebSocket bağlantı yönetimi
│   │   └── rate_limiter.py           # Redis tabanlı rate limiter
│   │
│   ├── brokers/                      # Broker adapter'ları
│   │   ├── __init__.py
│   │   ├── base.py                   # AbstractBroker (abstract class)
│   │   ├── paper_broker.py           # Paper trading simülasyonu
│   │   ├── is_yatirim.py             # İş Yatırım API adapter
│   │   └── factory.py                # Broker factory
│   │
│   ├── strategies/                   # Strateji implementasyonları
│   │   ├── __init__.py
│   │   ├── base.py                   # BaseStrategy abstract class
│   │   ├── ma_crossover.py           # Moving Average Crossover
│   │   ├── rsi_reversal.py           # RSI Mean Reversion
│   │   ├── macd_signal.py            # MACD Signal
│   │   ├── bollinger_breakout.py     # Bollinger Breakout
│   │   ├── momentum_ranker.py        # Momentum Ranking
│   │   └── registry.py               # Strateji kayıt sistemi
│   │
│   ├── indicators/                   # Teknik gösterge hesaplamaları
│   │   ├── __init__.py
│   │   ├── trend.py                  # SMA, EMA, ADX, Parabolic SAR
│   │   ├── momentum.py               # RSI, MACD, Stochastic, CCI
│   │   ├── volatility.py             # Bollinger Bands, ATR, Keltner
│   │   ├── volume.py                 # OBV, VWAP, MFI
│   │   └── utils.py                  # Yardımcı fonksiyonlar
│   │
│   ├── tasks/                        # Celery görevleri
│   │   ├── __init__.py
│   │   ├── celery_app.py             # Celery uygulama yapılandırması
│   │   ├── market_tasks.py           # Veri çekme görevleri
│   │   ├── strategy_tasks.py         # Strateji çalıştırma görevleri
│   │   ├── backtest_tasks.py         # Backtest görevleri
│   │   ├── notification_tasks.py     # Bildirim gönderme görevleri
│   │   ├── ml_tasks.py               # Model eğitim görevleri
│   │   └── maintenance_tasks.py      # Bakım görevleri (cleanup, snapshot)
│   │
│   ├── websocket/                    # WebSocket endpoint'leri
│   │   ├── __init__.py
│   │   ├── market_stream.py          # /ws/v1/market/stream
│   │   └── notification_stream.py    # /ws/v1/notifications
│   │
│   └── utils/                        # Yardımcı fonksiyonlar
│       ├── __init__.py
│       ├── formatters.py             # Para, tarih formatlama
│       ├── validators.py             # Özel validasyon fonksiyonları
│       └── constants.py              # Sabitler (BIST seans saatleri vb.)
│
├── scripts/                          # Yönetim scriptleri
│   ├── seed_symbols.py               # Sembol ve endeks verisi yükle
│   ├── seed_historical.py            # Geçmiş fiyat verisi yükle
│   └── create_admin.py               # Admin kullanıcı oluştur
│
└── tests/                            # Test dosyaları
    ├── __init__.py
    ├── conftest.py                   # fixture'lar, test DB setup
    ├── factories.py                  # factory-boy model factory'leri
    ├── unit/
    │   ├── __init__.py
    │   ├── test_security.py
    │   ├── test_indicators.py
    │   ├── test_strategies.py
    │   ├── test_risk_service.py
    │   └── test_formatters.py
    ├── integration/
    │   ├── __init__.py
    │   ├── test_auth_api.py
    │   ├── test_market_api.py
    │   ├── test_orders_api.py
    │   ├── test_portfolio_api.py
    │   └── test_backtest_api.py
    └── fixtures/
        ├── market_data.json          # Test piyasa verisi
        └── strategies.json           # Test strateji konfigürasyonları
```

---

## 2. Ortam Değişkenleri ve Yapılandırma

### 2.1 app/config.py — Settings Sınıfı

```python
"""Ortam değişkenleri yönetimi — Pydantic Settings ile tip güvenli yapılandırma."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr
from functools import lru_cache


class Settings(BaseSettings):
    """Tüm ortam değişkenleri bu sınıftan okunur. .env dosyası otomatik yüklenir."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Uygulama ──
    APP_NAME: str = "bist-robogo"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development | staging | production
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # ── Veritabanı ──
    DATABASE_URL: str = "postgresql+asyncpg://bist:bist_secret@localhost:5432/bist_robogo"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_ECHO: bool = False

    # ── Redis ──
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 300  # saniye

    # ── Kafka ──
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_GROUP_ID: str = "bist-robogo"

    # ── JWT ──
    JWT_SECRET_KEY: SecretStr = SecretStr("change-me-in-production-32chars!")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Broker ──
    BROKER_ENCRYPTION_KEY: SecretStr = SecretStr("32-byte-encryption-key-change-me")

    # ── Email ──
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: SecretStr = SecretStr("")
    SMTP_FROM_EMAIL: str = "noreply@bist-robogo.com"

    # ── Telegram ──
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_DEFAULT_CHAT_ID: str = ""

    # ── Monitoring ──
    SENTRY_DSN: str = ""
    LOG_LEVEL: str = "INFO"

    # ── MLflow ──
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"

    # ── MinIO / S3 ──
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: SecretStr = SecretStr("minioadmin")

    # ── Data ──
    DEFAULT_HISTORICAL_YEARS: int = 5  # Kaç yıllık geçmiş veri çekilecek
    MARKET_OPEN_HOUR: int = 10  # BIST açılış 10:00
    MARKET_CLOSE_HOUR: int = 18  # BIST kapanış 18:00


@lru_cache
def get_settings() -> Settings:
    """Singleton Settings instance. İlk çağrıda oluşturulur, sonraki çağrılarda cache'ten döner."""
    return Settings()
```

---

## 3. Veritabanı Bağlantı Yönetimi

### 3.1 app/database.py

```python
"""SQLAlchemy async engine, session factory ve Base model."""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings

settings = get_settings()

# ── Async Engine ──
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,  # Bağlantı sağlık kontrolü
)

# ── Session Factory ──
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Tüm ORM modellerinin temel sınıfı."""
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency: Her request için yeni session açar, sonunda kapatır.

    Kullanım:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

---

## 4. ORM Model Temeli

### 4.1 app/models/base.py

```python
"""Tüm modellerde ortak olan alanlar için mixin."""

import uuid
from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID


class TimestampMixin:
    """created_at ve updated_at alanları ekler."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class UUIDMixin:
    """UUID primary key ekler."""
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
```

### 4.2 app/models/user.py

```python
"""Kullanıcı ve API anahtarı ORM modelleri."""

import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="viewer", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    two_factor_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # İlişkiler
    api_keys: Mapped[list["ApiKey"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    broker_connections: Mapped[list["BrokerConnection"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    strategies: Mapped[list["Strategy"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    orders: Mapped[list["Order"]] = relationship(back_populates="user")
    portfolio: Mapped["Portfolio"] = relationship(back_populates="user", uselist=False)

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class ApiKey(Base, UUIDMixin):
    __tablename__ = "api_keys"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    permissions: Mapped[dict] = mapped_column(JSONB, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")

    user: Mapped["User"] = relationship(back_populates="api_keys")
```

### 4.3 app/models/**init**.py

```python
"""ORM model re-export. Alembic ve uygulama bu dosyayı import eder."""

from app.models.base import UUIDMixin, TimestampMixin
from app.models.user import User, ApiKey
from app.models.broker import BrokerConnection
from app.models.market import Symbol, BistIndex, IndexComponent
from app.models.strategy import Strategy, Signal
from app.models.order import Order, Trade
from app.models.portfolio import Portfolio, Position, PortfolioSnapshot
from app.models.risk import RiskRule, RiskEvent
from app.models.backtest import BacktestRun, BacktestTrade
from app.models.notification import Notification
from app.models.audit import AuditLog

__all__ = [
    "User", "ApiKey",
    "BrokerConnection",
    "Symbol", "BistIndex", "IndexComponent",
    "Strategy", "Signal",
    "Order", "Trade",
    "Portfolio", "Position", "PortfolioSnapshot",
    "RiskRule", "RiskEvent",
    "BacktestRun", "BacktestTrade",
    "Notification",
    "AuditLog",
]
```

> **Not:** Her ORM modeli (broker.py, market.py, strategy.py, order.py, portfolio.py, risk.py, backtest.py, notification.py, audit.py) 03-VERI-MODELLERI-VE-API.md dokümanındaki SQL şemalarının SQLAlchemy 2.0 mapped_column formatına dönüştürülmüş halidir. Yukarıdaki `user.py` örneğini takip ederek oluşturulmalıdır.

---

## 5. FastAPI Uygulama Fabrikası

### 5.1 app/main.py

```python
"""FastAPI uygulama fabrikası — tüm middleware, router ve event handler'ları burada bağlanır."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.config import get_settings
from app.api.router import api_router
from app.api.health import health_router
from app.middleware import RequestLoggingMiddleware, RateLimitMiddleware
from app.logging_config import setup_logging
from app.core.redis_client import redis_manager
from app.database import engine


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
```

---

## 6. Middleware

### 6.1 app/middleware.py

```python
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

        # Structlog'a request context ekle
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
                    }
                },
            )

        return await call_next(request)
```

---

## 7. Exception Handling

### 7.1 app/exceptions.py

```python
"""Custom exception sınıfları ve global exception handler."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import structlog

logger = structlog.get_logger()


# ── Custom Exception Sınıfları ──

class AppException(Exception):
    """Temel uygulama exception sınıfı."""
    def __init__(self, code: str, message: str, status_code: int = 400, details: dict | None = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class NotFoundException(AppException):
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} bulunamadı: {resource_id}",
            status_code=404,
        )


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Kimlik doğrulama gerekli"):
        super().__init__(code="UNAUTHORIZED", message=message, status_code=401)


class ForbiddenException(AppException):
    def __init__(self, message: str = "Bu işlem için yetkiniz yok"):
        super().__init__(code="FORBIDDEN", message=message, status_code=403)


class ConflictException(AppException):
    def __init__(self, message: str):
        super().__init__(code="CONFLICT", message=message, status_code=409)


class RiskLimitExceededException(AppException):
    def __init__(self, message: str, details: dict):
        super().__init__(
            code="RISK_LIMIT_EXCEEDED",
            message=message,
            status_code=422,
            details=details,
        )


class InsufficientBalanceException(AppException):
    def __init__(self, required: float, available: float):
        super().__init__(
            code="INSUFFICIENT_BALANCE",
            message="Yetersiz bakiye",
            status_code=422,
            details={"required": required, "available": available},
        )


class MarketClosedException(AppException):
    def __init__(self):
        super().__init__(
            code="MARKET_CLOSED",
            message="Piyasa şu anda kapalı",
            status_code=422,
        )


class BrokerException(AppException):
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(
            code="BROKER_ERROR",
            message=message,
            status_code=502,
            details=details or {},
        )


# ── Global Exception Handler'lar ──

def register_exception_handlers(app: FastAPI) -> None:
    """FastAPI uygulamasına global exception handler'ları ekler."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        logger.warning("app_exception", code=exc.code, message=exc.message, details=exc.details)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                },
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            })
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "İstek doğrulama hatası",
                    "details": {"errors": errors},
                },
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("unhandled_exception", error=str(exc), exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Beklenmeyen bir hata oluştu",
                },
            },
        )
```

> **Not:** `register_exception_handlers(app)` çağrısı `create_app()` içinde `app` oluşturulduktan sonra yapılmalıdır.

---

## 8. Güvenlik (JWT + Password)

### 8.1 app/core/security.py

```python
"""JWT token yönetimi ve şifre hash/doğrulama."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings

settings = get_settings()

# ── Password Hashing ──
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Düz metin şifreyi bcrypt ile hash'ler."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Düz metin şifreyi hash ile karşılaştırır."""
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT Token ──

def create_access_token(user_id: UUID, role: str) -> str:
    """Access token oluşturur.

    Payload:
        sub: str (user_id)
        role: str
        exp: datetime
        type: "access"
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY.get_secret_value(), algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: UUID) -> str:
    """Refresh token oluşturur.

    Payload:
        sub: str (user_id)
        exp: datetime
        type: "refresh"
    """
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY.get_secret_value(), algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """JWT token'ı decode eder. Geçersizse JWTError fırlatır.

    Returns:
        dict: Token payload (sub, role, exp, type)

    Raises:
        JWTError: Token geçersiz veya süresi dolmuş
    """
    return jwt.decode(token, settings.JWT_SECRET_KEY.get_secret_value(), algorithms=[settings.JWT_ALGORITHM])
```

---

## 9. FastAPI Dependencies

### 9.1 app/dependencies.py

```python
"""FastAPI dependency injection fonksiyonları."""

from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from app.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.schemas.auth import TokenPayload

security_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """JWT token'dan mevcut kullanıcıyı çözümler.

    Kullanım:
        @router.get("/me")
        async def me(user: User = Depends(get_current_user)):
            return user
    """
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz token tipi")

        user_id = UUID(payload["sub"])
    except (JWTError, ValueError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz veya süresi dolmuş token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Kullanıcı bulunamadı veya deaktif")

    return user


def require_role(*roles: str):
    """Belirli rollere sahip kullanıcıları gerektirir.

    Kullanım:
        @router.post("/admin-action")
        async def admin(user: User = Depends(require_role("admin"))):
            ...
    """
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Bu işlem için şu rollerden biri gerekli: {', '.join(roles)}",
            )
        return user

    return role_checker


async def get_current_trader(user: User = Depends(get_current_user)) -> User:
    """Trader veya admin rolüne sahip kullanıcıyı gerektirir."""
    if user.role not in ("admin", "trader"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işlem için 'trader' veya 'admin' rolü gerekli",
        )
    return user
```

---

## 10. API Router Yapısı

### 10.1 app/api/router.py — Ana Router

```python
"""Tüm API v1 router'larını birleştirir."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.market import router as market_router
from app.api.v1.orders import router as orders_router
from app.api.v1.portfolio import router as portfolio_router
from app.api.v1.strategies import router as strategies_router
from app.api.v1.backtest import router as backtest_router
from app.api.v1.risk import router as risk_router
from app.api.v1.trends import router as trends_router
from app.api.v1.notifications import router as notifications_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(market_router, prefix="/market", tags=["market"])
api_router.include_router(orders_router, prefix="/orders", tags=["orders"])
api_router.include_router(portfolio_router, prefix="/portfolio", tags=["portfolio"])
api_router.include_router(strategies_router, prefix="/strategies", tags=["strategies"])
api_router.include_router(backtest_router, prefix="/backtest", tags=["backtest"])
api_router.include_router(risk_router, prefix="/risk", tags=["risk"])
api_router.include_router(trends_router, prefix="/analysis", tags=["trends"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
```

### 10.2 app/api/health.py — Health Check

```python
"""Sağlık kontrolü endpoint'leri."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database import get_db
from app.core.redis_client import redis_manager

health_router = APIRouter()


@health_router.get("/health")
async def health_check():
    """Basit health check — uygulama çalışıyor mu?"""
    return {"status": "healthy"}


@health_router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Readiness check — tüm bağımlılıklar hazır mı?

    Kontroller:
    1. PostgreSQL bağlantısı
    2. Redis bağlantısı
    """
    checks = {}

    # PostgreSQL
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"

    # Redis
    try:
        await redis_manager.client.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {str(e)}"

    all_ok = all(v == "ok" for v in checks.values())
    return {
        "status": "ready" if all_ok else "degraded",
        "checks": checks,
    }
```

### 10.3 app/api/v1/auth.py — Örnek Router Implementasyonu

```python
"""Kimlik doğrulama endpoint'leri."""

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    Enable2FAResponse,
    Verify2FARequest,
)
from app.schemas.common import APIResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=APIResponse[UserResponse], status_code=201)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Yeni kullanıcı kaydı.

    - Email benzersiz olmalı
    - Şifre min 8 karakter, 1 büyük harf, 1 rakam içermeli
    - Varsayılan rol: 'viewer'
    """
    service = AuthService(db)
    user = await service.register(body)
    return APIResponse(success=True, data=UserResponse.model_validate(user))


@router.post("/login", response_model=APIResponse[TokenResponse])
async def login(
    body: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Kullanıcı girişi.

    - Email + şifre doğrulama
    - 2FA aktifse TOTP kodu da gerekli
    - Access token (body) + Refresh token (httpOnly cookie) döner
    """
    service = AuthService(db)
    tokens = await service.login(body)

    # Refresh token'ı httpOnly cookie olarak set et
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,  # 7 gün
        path="/api/v1/auth",
    )

    return APIResponse(success=True, data=tokens)


@router.post("/refresh", response_model=APIResponse[TokenResponse])
async def refresh_token(
    response: Response,
    db: AsyncSession = Depends(get_db),
    # refresh_token cookie'den okunur
):
    """Access token yenileme (refresh token ile)."""
    # Cookie'den refresh token al
    from fastapi import Request
    # Not: refresh token, cookie'den Request.cookies üzerinden alınır
    pass  # Service implementasyonu


@router.post("/logout")
async def logout(
    response: Response,
    user: User = Depends(get_current_user),
):
    """Oturum kapatma — refresh token cookie'sini siler."""
    response.delete_cookie("refresh_token", path="/api/v1/auth")
    return APIResponse(success=True, data={"message": "Oturum kapatıldı"})


@router.get("/me", response_model=APIResponse[UserResponse])
async def get_me(user: User = Depends(get_current_user)):
    """Mevcut kullanıcı bilgilerini döner."""
    return APIResponse(success=True, data=UserResponse.model_validate(user))


@router.post("/2fa/enable", response_model=APIResponse[Enable2FAResponse])
async def enable_2fa(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """2FA etkinleştirme — TOTP secret + QR code URI döner."""
    service = AuthService(db)
    result = await service.enable_2fa(user)
    return APIResponse(success=True, data=result)


@router.post("/2fa/verify")
async def verify_2fa(
    body: Verify2FARequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """2FA doğrulama — TOTP kodu ile doğrulama."""
    service = AuthService(db)
    await service.verify_2fa(user, body.code)
    return APIResponse(success=True, data={"message": "2FA doğrulandı"})
```

---

## 11. Pydantic Şema Örnekleri

### 11.1 app/schemas/common.py

```python
"""Ortak API response şemaları."""

from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict = {}


class APIResponse(BaseModel, Generic[T]):
    """Standart API yanıt formatı.

    Tüm endpoint'ler bu formatı döner:
    {
        "success": true/false,
        "data": { ... },
        "meta": { ... } (opsiyonel)
    }
    """
    success: bool
    data: T | None = None
    error: ErrorDetail | None = None
    meta: PaginationMeta | None = None
```

### 11.2 app/schemas/auth.py

```python
"""Kimlik doğrulama şemaları."""

from pydantic import BaseModel, Field, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128, description="Min 8 karakter, 1 büyük harf, 1 rakam")
    full_name: str = Field(..., min_length=2, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    totp_code: str | None = Field(None, min_length=6, max_length=6, description="2FA aktifse gerekli")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # saniye
    refresh_token: str  # Cookie'de de set edilir


class Enable2FAResponse(BaseModel):
    secret: str
    qr_code_uri: str  # otpauth:// URI


class Verify2FARequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=6)
```

---

## 12. Service Katmanı Pattern

### 12.1 Genel Pattern

Her servis aşağıdaki pattern'i takip eder:

```python
"""Service template — tüm servisler bu pattern'i kullanır."""

from sqlalchemy.ext.asyncio import AsyncSession
import structlog

logger = structlog.get_logger()


class ExampleService:
    """Service sınıfı constructor'da DB session alır.

    Kurallar:
    1. İş mantığı burada olur (router'da değil)
    2. DB erişimi repository üzerinden yapılır (veya direkt session)
    3. Diğer servisleri __init__'te alabilir (DI)
    4. Exception fırlatır, router yakalar
    5. Loglama structlog ile yapılır
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, item_id: str):
        """Örnek: ID ile kayıt getir."""
        from app.models import ExampleModel
        from app.exceptions import NotFoundException

        result = await self.db.get(ExampleModel, item_id)
        if not result:
            raise NotFoundException("ExampleModel", item_id)
        return result

    async def create(self, data: dict):
        """Örnek: Yeni kayıt oluştur."""
        from app.models import ExampleModel

        instance = ExampleModel(**data)
        self.db.add(instance)
        await self.db.flush()  # ID almak için
        logger.info("example_created", id=str(instance.id))
        return instance
```

### 12.2 Repository Pattern (Opsiyonel — Karmaşık sorgular için)

```python
"""Base repository — generic CRUD işlemleri."""

from typing import TypeVar, Generic, Type
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    def __init__(self, model: Type[ModelT], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id: UUID) -> ModelT | None:
        return await self.db.get(self.model, id)

    async def get_all(self, skip: int = 0, limit: int = 20) -> list[ModelT]:
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count(self) -> int:
        stmt = select(func.count()).select_from(self.model)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def create(self, **kwargs) -> ModelT:
        instance = self.model(**kwargs)
        self.db.add(instance)
        await self.db.flush()
        return instance

    async def update(self, instance: ModelT, **kwargs) -> ModelT:
        for key, value in kwargs.items():
            setattr(instance, key, value)
        await self.db.flush()
        return instance

    async def delete(self, instance: ModelT) -> None:
        await self.db.delete(instance)
        await self.db.flush()
```

---

## 13. Redis Yönetimi

### 13.1 app/core/redis_client.py

```python
"""Redis bağlantı yöneticisi."""

import redis.asyncio as redis
from app.config import get_settings

settings = get_settings()


class RedisManager:
    """Redis bağlantısını yönetir. Uygulama başlangıcında connect(), kapanışta disconnect() çağrılır."""

    def __init__(self):
        self.client: redis.Redis | None = None

    async def connect(self):
        """Redis'e bağlan."""
        self.client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        await self.client.ping()

    async def disconnect(self):
        """Redis bağlantısını kapat."""
        if self.client:
            await self.client.close()

    async def get_cached(self, key: str) -> str | None:
        """Cache'ten veri oku."""
        return await self.client.get(key)

    async def set_cached(self, key: str, value: str, ttl: int | None = None):
        """Cache'e veri yaz."""
        ttl = ttl or settings.REDIS_CACHE_TTL
        await self.client.set(key, value, ex=ttl)

    async def delete_cached(self, key: str):
        """Cache'ten veri sil."""
        await self.client.delete(key)

    async def publish(self, channel: str, message: str):
        """Pub/Sub mesaj gönder."""
        await self.client.publish(channel, message)


# Singleton instance
redis_manager = RedisManager()
```

---

## 14. Rate Limiter

### 14.1 app/core/rate_limiter.py

```python
"""Redis tabanlı sliding window rate limiter."""

from app.core.redis_client import redis_manager


async def check_rate_limit(key: str, max_requests: int = 60, window_seconds: int = 60) -> bool:
    """Sliding window rate limit kontrolü.

    Args:
        key: Rate limit anahtarı (genelde IP veya user_id)
        max_requests: Pencere içinde izin verilen maksimum istek
        window_seconds: Pencere süresi (saniye)

    Returns:
        bool: True ise istek izinli, False ise limit aşılmış
    """
    redis_key = f"rate:limit:{key}"

    try:
        current = await redis_manager.client.incr(redis_key)
        if current == 1:
            await redis_manager.client.expire(redis_key, window_seconds)
        return current <= max_requests
    except Exception:
        # Redis erişilemiyorsa izin ver (fail-open)
        return True
```

---

## 15. WebSocket Yönetimi

### 15.1 app/core/websocket_manager.py

```python
"""WebSocket bağlantı yöneticisi — channel-based pub/sub."""

import json
from typing import Any
from fastapi import WebSocket
import structlog

logger = structlog.get_logger()


class WebSocketManager:
    """WebSocket bağlantılarını channel bazlı yönetir.

    Kanallar:
    - quote:{symbol} → Fiyat güncellemeleri
    - orderbook:{symbol} → Order book güncellemeleri
    - signal → Strateji sinyalleri
    - notification:{user_id} → Kullanıcı bildirimleri
    """

    def __init__(self):
        # channel_name → set of WebSocket connections
        self.channels: dict[str, set[WebSocket]] = {}
        # websocket → set of channel names (cleanup için)
        self.connections: dict[WebSocket, set[str]] = {}

    async def connect(self, websocket: WebSocket):
        """WebSocket bağlantısını kabul et."""
        await websocket.accept()
        self.connections[websocket] = set()
        logger.info("ws_connected", client=id(websocket))

    def disconnect(self, websocket: WebSocket):
        """WebSocket bağlantısını kaldır ve tüm kanallardan çıkar."""
        channels = self.connections.pop(websocket, set())
        for channel in channels:
            self.channels.get(channel, set()).discard(websocket)
            if not self.channels.get(channel):
                self.channels.pop(channel, None)
        logger.info("ws_disconnected", client=id(websocket))

    def subscribe(self, websocket: WebSocket, channel: str):
        """WebSocket'i bir kanala abone et."""
        if channel not in self.channels:
            self.channels[channel] = set()
        self.channels[channel].add(websocket)
        self.connections[websocket].add(channel)

    def unsubscribe(self, websocket: WebSocket, channel: str):
        """WebSocket'i bir kanaldan çıkar."""
        self.channels.get(channel, set()).discard(websocket)
        self.connections.get(websocket, set()).discard(channel)

    async def broadcast(self, channel: str, data: dict[str, Any]):
        """Bir kanaldaki tüm bağlantılara mesaj gönder."""
        message = json.dumps({"channel": channel, "data": data})
        dead_connections = []

        for ws in self.channels.get(channel, set()):
            try:
                await ws.send_text(message)
            except Exception:
                dead_connections.append(ws)

        # Kopan bağlantıları temizle
        for ws in dead_connections:
            self.disconnect(ws)

    async def send_personal(self, websocket: WebSocket, data: dict[str, Any]):
        """Tek bir bağlantıya mesaj gönder."""
        await websocket.send_json(data)


# Singleton instance
ws_manager = WebSocketManager()
```

### 15.2 app/websocket/market_stream.py

```python
"""WebSocket piyasa veri akışı endpoint'i."""

import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket_manager import ws_manager
import structlog

logger = structlog.get_logger()

router = APIRouter()


@router.websocket("/ws/v1/market/stream")
async def market_stream(websocket: WebSocket):
    """Piyasa verisi WebSocket stream.

    Client mesaj formatı:
        {"action": "subscribe", "channels": ["quote:THYAO", "orderbook:GARAN"]}
        {"action": "unsubscribe", "channels": ["quote:THYAO"]}

    Server mesaj formatı:
        {"channel": "quote:THYAO", "data": {...}}
    """
    await ws_manager.connect(websocket)

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                message = json.loads(raw)
                action = message.get("action")
                channels = message.get("channels", [])

                if action == "subscribe":
                    for ch in channels:
                        ws_manager.subscribe(websocket, ch)
                    await ws_manager.send_personal(websocket, {
                        "type": "subscribed",
                        "channels": channels,
                    })

                elif action == "unsubscribe":
                    for ch in channels:
                        ws_manager.unsubscribe(websocket, ch)
                    await ws_manager.send_personal(websocket, {
                        "type": "unsubscribed",
                        "channels": channels,
                    })

            except json.JSONDecodeError:
                await ws_manager.send_personal(websocket, {
                    "type": "error",
                    "message": "Geçersiz JSON formatı",
                })

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
```

---

## 16. Celery Yapılandırması

### 16.1 app/tasks/celery_app.py

```python
"""Celery uygulama yapılandırması."""

from celery import Celery
from celery.schedules import crontab

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "bist_robogo",
    broker=settings.REDIS_URL.replace("/0", "/1"),  # Redis DB 1 (broker)
    backend=settings.REDIS_URL.replace("/0", "/2"),   # Redis DB 2 (result)
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Europe/Istanbul",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,        # 1 saat maks
    task_soft_time_limit=3000,   # 50 dk soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# ── Otomatik task keşfi ──
celery_app.autodiscover_tasks([
    "app.tasks.market_tasks",
    "app.tasks.strategy_tasks",
    "app.tasks.backtest_tasks",
    "app.tasks.notification_tasks",
    "app.tasks.ml_tasks",
    "app.tasks.maintenance_tasks",
])

# ── Beat Schedule (Zamanlı Görevler) ──
celery_app.conf.beat_schedule = {
    # Günlük EOD veri güncelleme — BIST kapanış sonrası
    "daily-eod-update": {
        "task": "app.tasks.market_tasks.fetch_eod_data",
        "schedule": crontab(hour=18, minute=30, day_of_week="1-5"),
    },
    # Portföy snapshot — her gün 18:00
    "daily-portfolio-snapshot": {
        "task": "app.tasks.maintenance_tasks.take_portfolio_snapshots",
        "schedule": crontab(hour=18, minute=0, day_of_week="1-5"),
    },
    # Günlük risk raporu — her gün 18:45
    "daily-risk-report": {
        "task": "app.tasks.notification_tasks.send_daily_risk_report",
        "schedule": crontab(hour=18, minute=45, day_of_week="1-5"),
    },
    # Haftalık model yeniden eğitim — Pazar 02:00
    "weekly-model-retrain": {
        "task": "app.tasks.ml_tasks.retrain_all_models",
        "schedule": crontab(hour=2, minute=0, day_of_week=0),
    },
    # Haftalık endeks bileşen güncelleme — Pazartesi 08:00
    "weekly-index-update": {
        "task": "app.tasks.market_tasks.update_index_components",
        "schedule": crontab(hour=8, minute=0, day_of_week=1),
    },
    # Veritabanı bakım — Pazar gece 03:00
    "weekly-db-maintenance": {
        "task": "app.tasks.maintenance_tasks.database_maintenance",
        "schedule": crontab(hour=3, minute=0, day_of_week=0),
    },
}
```

### 16.2 app/tasks/market_tasks.py — Örnek Task

```python
"""Piyasa verisi Celery görevleri."""

from app.tasks.celery_app import celery_app
import structlog

logger = structlog.get_logger()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_eod_data(self):
    """Günlük kapanış (EOD) verilerini tüm semboller için çek ve kaydet.

    Adımlar:
    1. Aktif sembolleri DB'den al
    2. yfinance üzerinden EOD OHLCV çek
    3. TimescaleDB ohlcv_1m tablosuna yaz
    4. Redis cache güncelle
    5. Başarı/hata logla
    """
    import asyncio
    from app.services.market_data_service import MarketDataService

    async def _run():
        from app.database import async_session_factory
        async with async_session_factory() as db:
            service = MarketDataService(db)
            result = await service.fetch_and_store_eod_data()
            logger.info("eod_data_fetched", symbols_updated=result["count"])
            return result

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("eod_data_fetch_failed", error=str(exc))
        raise self.retry(exc=exc)
```

---

## 17. Broker Adapter Pattern

### 17.1 app/brokers/base.py

```python
"""Broker adapter abstract base class."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class BrokerOrderStatus(str, Enum):
    SUBMITTED = "submitted"
    FILLED = "filled"
    PARTIAL_FILL = "partial_fill"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class BrokerOrderResult:
    broker_order_id: str
    status: BrokerOrderStatus
    filled_quantity: int
    filled_price: Decimal | None
    message: str = ""


@dataclass
class BrokerQuote:
    symbol: str
    price: Decimal
    bid: Decimal
    ask: Decimal
    volume: int


class AbstractBroker(ABC):
    """Tüm broker adapter'ların implement etmesi gereken arayüz."""

    @abstractmethod
    async def connect(self) -> bool:
        """Broker'a bağlan. Başarılıysa True döner."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Broker bağlantısını kapat."""
        pass

    @abstractmethod
    async def submit_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: int,
        price: Decimal | None = None,
        stop_price: Decimal | None = None,
    ) -> BrokerOrderResult:
        """Emir gönder."""
        pass

    @abstractmethod
    async def cancel_order(self, broker_order_id: str) -> BrokerOrderResult:
        """Emir iptal et."""
        pass

    @abstractmethod
    async def get_order_status(self, broker_order_id: str) -> BrokerOrderResult:
        """Emir durumu sorgula."""
        pass

    @abstractmethod
    async def get_quote(self, symbol: str) -> BrokerQuote:
        """Anlık fiyat bilgisi al."""
        pass

    @abstractmethod
    async def get_positions(self) -> list[dict]:
        """Açık pozisyonları al."""
        pass
```

### 17.2 app/brokers/paper_broker.py

```python
"""Paper trading broker — gerçek emir göndermeden simülasyon yapar."""

from decimal import Decimal
from uuid import uuid4
import structlog

from app.brokers.base import AbstractBroker, BrokerOrderResult, BrokerOrderStatus, BrokerQuote
from app.core.redis_client import redis_manager

logger = structlog.get_logger()


class PaperBroker(AbstractBroker):
    """Paper trading simülasyonu.

    - Tüm emirler anında 'filled' olur.
    - Fiyat Redis cache'ten alınır (gerçek piyasa fiyatı).
    - Slippage simülasyonu: mevcut fiyata %0.05 eklenir/çıkarılır.
    """

    SLIPPAGE_RATE = Decimal("0.0005")  # %0.05

    async def connect(self) -> bool:
        logger.info("paper_broker_connected")
        return True

    async def disconnect(self) -> None:
        logger.info("paper_broker_disconnected")

    async def submit_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: int,
        price: Decimal | None = None,
        stop_price: Decimal | None = None,
    ) -> BrokerOrderResult:
        """Paper order — anında fill."""

        # Redis'ten gerçek fiyatı al
        quote = await self.get_quote(symbol)
        fill_price = quote.price

        # Slippage uygula
        if side == "buy":
            fill_price = fill_price * (1 + self.SLIPPAGE_RATE)
        else:
            fill_price = fill_price * (1 - self.SLIPPAGE_RATE)

        # Limit order ise fiyat kontrolü
        if order_type == "limit" and price:
            if side == "buy" and quote.price > price:
                return BrokerOrderResult(
                    broker_order_id=str(uuid4()),
                    status=BrokerOrderStatus.SUBMITTED,
                    filled_quantity=0,
                    filled_price=None,
                    message="Limit fiyat bekleniyor",
                )
            if side == "sell" and quote.price < price:
                return BrokerOrderResult(
                    broker_order_id=str(uuid4()),
                    status=BrokerOrderStatus.SUBMITTED,
                    filled_quantity=0,
                    filled_price=None,
                    message="Limit fiyat bekleniyor",
                )

        return BrokerOrderResult(
            broker_order_id=f"PAPER-{uuid4().hex[:12].upper()}",
            status=BrokerOrderStatus.FILLED,
            filled_quantity=quantity,
            filled_price=fill_price,
            message="Paper trade executed",
        )

    async def cancel_order(self, broker_order_id: str) -> BrokerOrderResult:
        return BrokerOrderResult(
            broker_order_id=broker_order_id,
            status=BrokerOrderStatus.CANCELLED,
            filled_quantity=0,
            filled_price=None,
            message="Paper order cancelled",
        )

    async def get_order_status(self, broker_order_id: str) -> BrokerOrderResult:
        return BrokerOrderResult(
            broker_order_id=broker_order_id,
            status=BrokerOrderStatus.FILLED,
            filled_quantity=0,
            filled_price=None,
        )

    async def get_quote(self, symbol: str) -> BrokerQuote:
        """Redis cache'ten fiyat bilgisi al."""
        import json
        cached = await redis_manager.get_cached(f"market:quote:{symbol}")
        if cached:
            data = json.loads(cached)
            return BrokerQuote(
                symbol=symbol,
                price=Decimal(str(data["price"])),
                bid=Decimal(str(data.get("bid", data["price"]))),
                ask=Decimal(str(data.get("ask", data["price"]))),
                volume=data.get("volume", 0),
            )
        raise ValueError(f"Fiyat bilgisi bulunamadı: {symbol}")

    async def get_positions(self) -> list[dict]:
        return []
```

### 17.3 app/brokers/factory.py

```python
"""Broker factory — broker adına göre doğru adapter'ı döner."""

from app.brokers.base import AbstractBroker
from app.brokers.paper_broker import PaperBroker


def get_broker(broker_name: str, credentials: dict | None = None) -> AbstractBroker:
    """Broker adapter factory.

    Args:
        broker_name: 'paper', 'is_yatirim', 'gedik'
        credentials: Broker API kimlik bilgileri (şifresi çözülmüş)

    Returns:
        AbstractBroker implementasyonu
    """
    brokers = {
        "paper": PaperBroker,
        # "is_yatirim": IsYatirimBroker,  # Faz 2'de eklenecek
        # "gedik": GedikBroker,            # Faz 4'te eklenecek
    }

    broker_class = brokers.get(broker_name)
    if not broker_class:
        raise ValueError(f"Bilinmeyen broker: {broker_name}")

    return broker_class()
```

---

## 18. Teknik Gösterge Hesaplamaları

### 18.1 app/indicators/momentum.py (Örnek)

```python
"""Momentum göstergeleri: RSI, MACD, Stochastic."""

import numpy as np
import pandas as pd


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """RSI (Relative Strength Index) hesapla.

    Args:
        prices: Kapanış fiyatları serisi
        period: RSI periyodu (varsayılan: 14)

    Returns:
        RSI değerleri (0-100 arası)
    """
    delta = prices.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.ewm(alpha=1 / period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(
    prices: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """MACD (Moving Average Convergence Divergence) hesapla.

    Args:
        prices: Kapanış fiyatları serisi
        fast_period: Hızlı EMA periyodu
        slow_period: Yavaş EMA periyodu
        signal_period: Sinyal çizgisi periyodu

    Returns:
        (macd_line, signal_line, histogram)
    """
    ema_fast = prices.ewm(span=fast_period, adjust=False).mean()
    ema_slow = prices.ewm(span=slow_period, adjust=False).mean()

    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram


def calculate_stochastic(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    k_period: int = 14,
    d_period: int = 3,
) -> tuple[pd.Series, pd.Series]:
    """Stochastic Oscillator (%K ve %D) hesapla.

    Returns:
        (%K, %D)
    """
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()

    k = 100 * (close - lowest_low) / (highest_high - lowest_low)
    d = k.rolling(window=d_period).mean()

    return k, d
```

---

## 19. Loglama Yapılandırması

### 19.1 app/logging_config.py

```python
"""Structlog yapılandırması — JSON formatında yapılandırılmış loglama."""

import logging
import structlog


def setup_logging(log_level: str = "INFO"):
    """Structlog'u yapılandırır. Uygulama başlangıcında bir kez çağrılır.

    Geliştirmede: Renkli konsol çıktısı
    Prodüksiyonda: JSON formatında çıktı
    """
    from app.config import get_settings
    settings = get_settings()

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.ENVIRONMENT == "production":
        # Prodüksiyon: JSON
        renderer = structlog.processors.JSONRenderer()
    else:
        # Geliştirme: Renkli konsol
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Gürültülü library'leri sessizleştir
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
```

---

## 20. Alembic Yapılandırması

### 20.1 alembic.ini

```ini
[alembic]
script_location = alembic
prepend_sys_path = .
sqlalchemy.url = driver://user:pass@localhost/dbname
# Not: Gerçek URL env.py'de ayarlanır, bu satır override edilir.

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

### 20.2 alembic/env.py

```python
"""Alembic migration ortam yapılandırması."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.config import get_settings
from app.database import Base
from app.models import *  # noqa: F401,F403 — Tüm modelleri import et

settings = get_settings()
config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Offline migration (SQL dosyası üretir)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Async migration."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Online migration."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

---

## 21. pyproject.toml

```toml
[tool.poetry]
name = "bist-robogo-backend"
version = "0.1.0"
description = "BIST İçin AI Destekli Otomatik Ticaret Platformu — Backend"
authors = ["bist-robogo team"]
readme = "README.md"
packages = [{include = "app"}]

[tool.poetry.dependencies]
python = "^3.12"

# Core Web Framework
fastapi = "^0.115.0"
uvicorn = {version = "^0.34.0", extras = ["standard"]}
pydantic = "^2.10.0"
pydantic-settings = "^2.7.0"
python-multipart = "^0.0.18"

# Database
sqlalchemy = {version = "^2.0.0", extras = ["asyncio"]}
asyncpg = "^0.30.0"
alembic = "^1.14.0"
psycopg = {version = "^3.2.0", extras = ["binary"]}

# Redis
redis = {version = "^5.2.0", extras = ["hiredis"]}

# Celery
celery = {version = "^5.4.0", extras = ["redis"]}

# Auth & Security
python-jose = {version = "^3.3.0", extras = ["cryptography"]}
passlib = {version = "^1.7.4", extras = ["bcrypt"]}
pyotp = "^2.9.0"

# Data & ML
pandas = "^2.2.0"
numpy = "^2.1.0"
scikit-learn = "^1.6.0"
yfinance = "^0.2.0"

# HTTP Client
httpx = "^0.28.0"
aiohttp = "^3.11.0"
websockets = "^14.0"

# Messaging
confluent-kafka = "^2.6.0"

# Logging & Monitoring
structlog = "^24.4.0"
sentry-sdk = {version = "^2.19.0", extras = ["fastapi"]}
prometheus-fastapi-instrumentator = "^7.0.0"

# Utilities
python-dateutil = "^2.9.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.3.0"
pytest-asyncio = "^0.24.0"
pytest-cov = "^6.0.0"
httpx = "^0.28.0"
factory-boy = "^3.3.0"
ruff = "^0.8.0"
mypy = "^1.13.0"
pre-commit = "^4.0.0"

[tool.poetry.group.ml.dependencies]
xgboost = "^2.1.0"
lightgbm = "^4.5.0"
torch = "^2.5.0"
optuna = "^4.1.0"
mlflow = "^2.19.0"
onnxruntime = "^1.20.0"
ta-lib = "^0.5.0"
pandas-ta = "^0.3.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = "-v --tb=short --cov=app --cov-report=term-missing"
filterwarnings = ["ignore::DeprecationWarning"]

[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
```

---

## 22. Dockerfile

```dockerfile
# ── Stage 1: Builder ──
FROM python:3.12-slim AS builder

WORKDIR /app

RUN pip install --no-cache-dir poetry==1.8.4

COPY pyproject.toml poetry.lock ./

# Virtualenv oluşturmadan paketleri kur
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

COPY . .

# ── Stage 2: Runtime ──
FROM python:3.12-slim AS runtime

WORKDIR /app

# Gerekli sistem paketleri
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Builder'dan paketleri kopyala
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# Non-root user
RUN adduser --disabled-password --gecos '' appuser
USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

# Uvicorn başlat
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

---

## 23. Seed Data Script

### 23.1 scripts/seed_symbols.py

```python
"""BIST sembol ve endeks verilerini veritabanına yükler.

Kullanım: python -m scripts.seed_symbols
"""

import asyncio
from app.database import async_session_factory
from app.models.market import Symbol, BistIndex, IndexComponent

# BIST 30 Sembolleri (Mart 2026 tahmini — gerçek listeye göre güncellenmeli)
BIST_30_SYMBOLS = [
    {"ticker": "AKBNK", "name": "Akbank", "sector": "Bankacılık"},
    {"ticker": "ARCLK", "name": "Arçelik", "sector": "Dayanıklı Tüketim"},
    {"ticker": "ASELS", "name": "Aselsan", "sector": "Savunma"},
    {"ticker": "BIMAS", "name": "BİM Mağazalar", "sector": "Perakende"},
    {"ticker": "EKGYO", "name": "Emlak Konut GYO", "sector": "GYO"},
    {"ticker": "EREGL", "name": "Ereğli Demir Çelik", "sector": "Metal"},
    {"ticker": "FROTO", "name": "Ford Otosan", "sector": "Otomotiv"},
    {"ticker": "GARAN", "name": "Garanti BBVA", "sector": "Bankacılık"},
    {"ticker": "GUBRF", "name": "Gübre Fabrikaları", "sector": "Kimya"},
    {"ticker": "HEKTS", "name": "Hektaş", "sector": "Kimya"},
    {"ticker": "ISCTR", "name": "İş Bankası C", "sector": "Bankacılık"},
    {"ticker": "KCHOL", "name": "Koç Holding", "sector": "Holding"},
    {"ticker": "KOZAL", "name": "Koza Altın", "sector": "Madencilik"},
    {"ticker": "KOZAA", "name": "Koza Anadolu Metal", "sector": "Madencilik"},
    {"ticker": "KRDMD", "name": "Kardemir D", "sector": "Metal"},
    {"ticker": "MGROS", "name": "Migros", "sector": "Perakende"},
    {"ticker": "ODAS", "name": "Odaş Elektrik", "sector": "Enerji"},
    {"ticker": "OYAKC", "name": "Oyak Çimento", "sector": "Çimento"},
    {"ticker": "PETKM", "name": "Petkim", "sector": "Petrokimya"},
    {"ticker": "PGSUS", "name": "Pegasus", "sector": "Havacılık"},
    {"ticker": "SAHOL", "name": "Sabancı Holding", "sector": "Holding"},
    {"ticker": "SASA", "name": "SASA Polyester", "sector": "Kimya"},
    {"ticker": "SISE", "name": "Şişecam", "sector": "Cam"},
    {"ticker": "TAVHL", "name": "TAV Havalimanları", "sector": "Havacılık"},
    {"ticker": "TCELL", "name": "Turkcell", "sector": "Telekomünikasyon"},
    {"ticker": "THYAO", "name": "Türk Hava Yolları", "sector": "Havacılık"},
    {"ticker": "TKFEN", "name": "Tekfen Holding", "sector": "Holding"},
    {"ticker": "TOASO", "name": "Tofaş", "sector": "Otomotiv"},
    {"ticker": "TUPRS", "name": "Tüpraş", "sector": "Enerji"},
    {"ticker": "YKBNK", "name": "Yapı Kredi Bankası", "sector": "Bankacılık"},
]

# Endeksler
INDICES = [
    {"code": "XU030", "name": "BIST 30", "description": "BIST en büyük 30 şirket"},
    {"code": "XU100", "name": "BIST 100", "description": "BIST en büyük 100 şirket"},
    {"code": "XKTUM", "name": "Katılım Tüm", "description": "Katılım Endeksi Tüm"},
    {"code": "XUSIN", "name": "BIST Sınai", "description": "BIST Sınai Endeksi"},
    {"code": "XBANK", "name": "BIST Banka", "description": "BIST Banka Endeksi"},
]


async def seed():
    async with async_session_factory() as db:
        # Semboller
        for sym_data in BIST_30_SYMBOLS:
            symbol = Symbol(**sym_data, is_active=True)
            db.add(symbol)

        # Endeksler
        for idx_data in INDICES:
            index = BistIndex(**idx_data, is_active=True)
            db.add(index)

        await db.commit()
        print(f"✅ {len(BIST_30_SYMBOLS)} sembol ve {len(INDICES)} endeks yüklendi.")


if __name__ == "__main__":
    asyncio.run(seed())
```

---

## 24. Test Yapılandırması

### 24.1 tests/conftest.py

```python
"""Pytest fixture'ları — test DB, factory'ler, authenticated client."""

import asyncio
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.main import create_app
from app.database import Base, get_db
from app.core.security import hash_password, create_access_token
from app.models.user import User

# Test DB URL
TEST_DATABASE_URL = "postgresql+asyncpg://bist:bist_secret@localhost:5432/bist_robogo_test"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine():
    eng = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture
async def db(engine):
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def app(db):
    application = create_app()

    async def override_get_db():
        yield db

    application.dependency_overrides[get_db] = override_get_db
    return application


@pytest_asyncio.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def test_user(db) -> User:
    """Test kullanıcısı oluştur."""
    user = User(
        id=uuid4(),
        email="test@example.com",
        password_hash=hash_password("Test1234!"),
        full_name="Test User",
        role="trader",
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    await db.flush()
    return user


@pytest_asyncio.fixture
async def auth_client(client, test_user) -> AsyncClient:
    """Authenticated test client."""
    token = create_access_token(test_user.id, test_user.role)
    client.headers["Authorization"] = f"Bearer {token}"
    return client
```

---

## 25. Sabitler ve Yardımcı Fonksiyonlar

### 25.1 app/utils/constants.py

```python
"""Uygulama sabitleri."""

from datetime import time

# BIST Seans Saatleri (Türkiye saati, UTC+3)
BIST_OPENING_TIME = time(10, 0)   # 10:00
BIST_CLOSING_TIME = time(18, 0)   # 18:00
BIST_LUNCH_START = time(12, 30)   # 12:30
BIST_LUNCH_END = time(14, 0)      # 14:00

# BIST çalışma günleri (Pazartesi=0, Cuma=4)
BIST_TRADING_DAYS = {0, 1, 2, 3, 4}

# Varsayılan Risk Limitleri
DEFAULT_RISK_LIMITS = {
    "max_daily_loss_pct": 2.0,           # Portföyün %2'si
    "max_position_size_pct": 10.0,       # Portföyün %10'u
    "max_open_positions": 10,
    "stop_loss_required": True,
    "max_order_value": 50_000.0,         # TL
    "max_daily_orders": 50,
    "max_correlated_positions": 3,
}

# Desteklenen Timeframe'ler
TIMEFRAMES = ["1m", "5m", "15m", "1h", "4h", "1d", "1w", "1M"]

# Desteklenen Emir Tipleri
ORDER_TYPES = ["market", "limit", "stop_loss", "take_profit", "trailing_stop"]

# Desteklenen Roller
USER_ROLES = ["admin", "trader", "viewer", "api_user"]

# Komisyon oranları (varsayılan)
DEFAULT_COMMISSION_RATE = 0.001  # %0.1
DEFAULT_SLIPPAGE_RATE = 0.0005   # %0.05
```

### 25.2 app/utils/formatters.py

```python
"""Formatlama yardımcı fonksiyonları."""

from decimal import Decimal


def format_currency(amount: Decimal | float, symbol: str = "₺") -> str:
    """Para birimini formatla. Örnek: 1250000.50 → ₺1,250,000.50"""
    return f"{symbol}{amount:,.2f}"


def format_percentage(value: Decimal | float) -> str:
    """Yüzde formatla. Örnek: 1.56 → +1.56%"""
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f}%"


def format_volume(volume: int) -> str:
    """Hacim formatla. Örnek: 45230000 → 45.23M"""
    if volume >= 1_000_000_000:
        return f"{volume / 1_000_000_000:.2f}B"
    elif volume >= 1_000_000:
        return f"{volume / 1_000_000:.2f}M"
    elif volume >= 1_000:
        return f"{volume / 1_000:.1f}K"
    return str(volume)
```

---

## 26. Geliştirme Sırası (Backend)

AI Agent backend'i aşağıdaki sırada geliştirmelidir:

### Faz 0 Sırası:

1. `pyproject.toml` oluştur → `poetry install`
2. `app/config.py` → Settings sınıfı
3. `app/database.py` → Engine, session, Base
4. `app/models/base.py` → Mixin'ler
5. `app/models/` → Tüm ORM modelleri (user → market → strategy → order → portfolio → risk → backtest → notification → audit)
6. `alembic.ini` + `alembic/env.py` → `alembic revision --autogenerate -m "initial"`
7. `app/exceptions.py` → Exception sınıfları
8. `app/logging_config.py` → Structlog setup
9. `app/core/security.py` → JWT + password
10. `app/core/redis_client.py` → Redis manager
11. `app/middleware.py` → Logging + rate limit
12. `app/main.py` → App factory
13. `app/api/health.py` → Health check
14. `Dockerfile` → Docker image
15. `docker-compose.yml` → Tüm servisler (ayrı doküman)

### Faz 1 Sırası (MVP):

16. `app/dependencies.py` → Auth dependency'ler
17. `app/schemas/` → Tüm Pydantic şemaları
18. `app/services/auth_service.py` + `app/api/v1/auth.py`
19. `app/services/market_data_service.py` + `app/api/v1/market.py`
20. `app/indicators/` → Teknik göstergeler
21. `app/core/websocket_manager.py` + `app/websocket/market_stream.py`
22. `app/tasks/celery_app.py` + `app/tasks/market_tasks.py`
23. `scripts/seed_symbols.py` + `scripts/seed_historical.py`
24. `app/brokers/` → Paper broker
25. `app/services/trading_service.py` + `app/api/v1/orders.py`
26. `app/services/portfolio_service.py` + `app/api/v1/portfolio.py`
27. `app/services/risk_service.py` + `app/api/v1/risk.py`
28. `tests/conftest.py` + testler

---

_Bu doküman, bist-robogo projesinin backend geliştirme sürecinde AI Agent'ın takip edeceği tam referans kılavuzdur._
