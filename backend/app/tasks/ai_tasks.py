# Source: Doc 10 §Faz 3 Sprint 3.1 — AI Celery görevleri
"""AI analiz ve sinyal üretim Celery görevleri."""

import asyncio
import logging

import structlog

from app.tasks.celery_app import celery_app

logger = structlog.get_logger()


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60)
def run_ai_analysis(self, symbol: str, user_id: str | None = None):
    """Tek bir sembol için AI analizi çalıştır.

    Async AI servisini senkron Celery task'ında çağırır.
    """
    try:
        from app.core.openrouter_client import OpenRouterClient
        from app.services.ai_service import AIService

        async def _analyze():
            # Celery task'larında DB session kullanımı: hafif session
            from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
            from app.config import get_settings

            settings = get_settings()
            engine = create_async_engine(settings.DATABASE_URL, echo=False)
            async with AsyncSession(engine) as db:
                client = OpenRouterClient()
                service = AIService(db, client=client)
                result = await service.analyze_symbol(symbol)
                return result.model_dump()

        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(_analyze())
        finally:
            loop.close()

        logger.info("ai_analysis_completed", symbol=symbol, action=result.get("action"))
        return result

    except Exception as exc:
        logger.error("ai_analysis_failed", symbol=symbol, error=str(exc))
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=120)
def run_ai_signals_batch(self, symbols: list[str] | None = None, limit: int = 10):
    """Toplu AI sinyal üretimi.

    Birden fazla sembol için sinyaller üretir.
    Zamanlanmış görev olarak kullanılabilir (ör: her gün 18:00).
    """
    try:
        from app.core.openrouter_client import OpenRouterClient
        from app.services.ai_service import AIService

        async def _generate():
            from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
            from app.config import get_settings

            settings = get_settings()
            engine = create_async_engine(settings.DATABASE_URL, echo=False)
            async with AsyncSession(engine) as db:
                client = OpenRouterClient()
                service = AIService(db, client=client)
                result = await service.generate_signals(symbols=symbols, limit=limit)
                return result.model_dump()

        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(_generate())
        finally:
            loop.close()

        signal_count = len(result.get("signals", []))
        logger.info("ai_signals_batch_completed", signal_count=signal_count)
        return result

    except Exception as exc:
        logger.error("ai_signals_batch_failed", error=str(exc))
        raise self.retry(exc=exc)
