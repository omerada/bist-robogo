# Source: Doc 07 §2 — Ortam Değişkenleri (Pydantic Settings)
"""Ortam değişkenleri yönetimi — Pydantic Settings ile tip güvenli yapılandırma."""

from functools import lru_cache
from typing import Any

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> Any:
        """Virgülle ayrılmış string veya JSON listesi kabul et."""
        if isinstance(v, str):
            if v.startswith("["):
                import json
                return json.loads(v)
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # ── Veritabanı ── (Doc 11 Tutarsızlık #2: docker-compose değerlerini kullan)
    DATABASE_URL: str = "postgresql+asyncpg://bist_user:bist_dev_pass_2026@localhost:5432/bist_robogo"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_ECHO: bool = False

    # ── Redis ── (Doc 11 Tutarsızlık #3: parolalı kullan)
    REDIS_URL: str = "redis://:bist_redis_pass_2026@localhost:6379/0"
    REDIS_CACHE_TTL: int = 300  # saniye

    # ── Celery ── (Doc 11 Tutarsızlık #5: ayrı env var kullan)
    CELERY_BROKER_URL: str = "redis://:bist_redis_pass_2026@localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://:bist_redis_pass_2026@localhost:6379/2"

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

    # ── OpenRouter AI ──
    OPENROUTER_API_KEY: SecretStr = SecretStr("")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_DEFAULT_MODEL: str = "google/gemini-2.5-flash"  # varsayılan model
    OPENROUTER_MAX_TOKENS: int = 4096
    OPENROUTER_TEMPERATURE: float = 0.3  # düşük sıcaklık → tutarlı analiz
    OPENROUTER_TIMEOUT: int = 60  # saniye

    # ── MLflow ──
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"

    # ── MinIO / S3 ──
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: SecretStr = SecretStr("minioadmin")

    # ── Data ──
    DEFAULT_HISTORICAL_YEARS: int = 5
    MARKET_OPEN_HOUR: int = 10  # BIST açılış 10:00
    MARKET_CLOSE_HOUR: int = 18  # BIST kapanış 18:00


@lru_cache
def get_settings() -> Settings:
    """Singleton Settings instance. İlk çağrıda oluşturulur, sonraki çağrılarda cache'ten döner."""
    return Settings()
