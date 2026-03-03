# Source: Doc 10 §Faz 3 Sprint 3.1+3.2+3.3 — AI Celery görevleri
"""AI analiz, sinyal üretim, strateji çalıştırma, deney ve performans Celery görevleri."""

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
    Zamanlanmış görev olarak kullanılabilir (ör: her gün 19:00).
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


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60)
def run_ai_strategy(self, symbol: str, params: dict | None = None):
    """AI strateji ile tek sembol analizi.

    AIStrategy sınıfını kullanarak StrategySignal üretir.
    Sonuç diğer strateji sinyalleriyle aynı formatta döner.
    """
    try:
        import pandas as pd

        async def _run():
            from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
            from app.config import get_settings
            from app.repositories.market_repository import OHLCVRepository, SymbolRepository
            from app.strategies.ai_strategy import AIStrategy

            settings = get_settings()
            engine = create_async_engine(settings.DATABASE_URL, echo=False)
            async with AsyncSession(engine) as db:
                # OHLCV verisini çek (son 120 bar)
                ohlcv_repo = OHLCVRepository(db)
                symbol_repo = SymbolRepository(db)

                sym = await symbol_repo.get_by_ticker(symbol)
                if not sym:
                    return {"error": f"Sembol bulunamadı: {symbol}"}

                rows = await ohlcv_repo.get_ohlcv(sym.id, limit=120)
                if not rows:
                    return {"error": f"OHLCV verisi yok: {symbol}"}

                # DataFrame oluştur
                df = pd.DataFrame(
                    [{"open": r.open, "high": r.high, "low": r.low,
                      "close": r.close, "volume": r.volume} for r in rows]
                )

                strategy = AIStrategy()
                signal = await strategy.analyze(symbol, df, params)

                return {
                    "symbol": signal.symbol,
                    "signal_type": signal.signal_type.value,
                    "confidence": signal.confidence,
                    "target_price": str(signal.target_price) if signal.target_price else None,
                    "stop_loss": str(signal.stop_loss) if signal.stop_loss else None,
                    "take_profit": str(signal.take_profit) if signal.take_profit else None,
                    "reason": signal.reason,
                    "metadata": signal.metadata,
                }

        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(_run())
        finally:
            loop.close()

        logger.info(
            "ai_strategy_completed",
            symbol=symbol,
            signal_type=result.get("signal_type"),
        )
        return result

    except Exception as exc:
        logger.error("ai_strategy_failed", symbol=symbol, error=str(exc))
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=1, default_retry_delay=180)
def run_ai_strategy_batch(self, symbols: list[str] | None = None, limit: int = 30):
    """Toplu AI strateji çalıştırma — aktif sembollerde AIStrategy ile sinyal üretimi.

    Beat schedule ile günlük çalıştırılabilir.
    """
    try:
        import pandas as pd

        async def _run_batch():
            from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
            from app.config import get_settings
            from app.repositories.market_repository import OHLCVRepository, SymbolRepository
            from app.strategies.ai_strategy import AIStrategy

            settings = get_settings()
            engine = create_async_engine(settings.DATABASE_URL, echo=False)
            results = []

            async with AsyncSession(engine) as db:
                symbol_repo = SymbolRepository(db)
                ohlcv_repo = OHLCVRepository(db)

                if not symbols:
                    all_symbols = await symbol_repo.get_active_symbols(limit=limit)
                    symbol_list = [s.ticker for s in all_symbols[:limit]]
                else:
                    symbol_list = symbols[:limit]

                strategy = AIStrategy()

                for ticker in symbol_list:
                    try:
                        sym = await symbol_repo.get_by_ticker(ticker)
                        if not sym:
                            continue

                        rows = await ohlcv_repo.get_ohlcv(sym.id, limit=120)
                        if not rows or len(rows) < 10:
                            continue

                        df = pd.DataFrame(
                            [{"open": r.open, "high": r.high, "low": r.low,
                              "close": r.close, "volume": r.volume} for r in rows]
                        )

                        signal = await strategy.analyze(ticker, df)
                        results.append({
                            "symbol": signal.symbol,
                            "signal_type": signal.signal_type.value,
                            "confidence": signal.confidence,
                            "reason": signal.reason,
                        })
                    except Exception as e:
                        logger.warning("ai_strategy_symbol_failed", symbol=ticker, error=str(e))

            return {"signals": results, "total": len(results)}

        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(_run_batch())
        finally:
            loop.close()

        logger.info("ai_strategy_batch_completed", total=result.get("total", 0))
        return result

    except Exception as exc:
        logger.error("ai_strategy_batch_failed", error=str(exc))
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=120)
def run_ab_experiment(self, experiment_id: str, user_id: str):
    """A/B test deneyini asenkron çalıştır.

    API'den tetiklenen deneyi arka planda işler.
    """
    try:
        from uuid import UUID as _UUID

        async def _run():
            from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

            from app.config import get_settings
            from app.services.ai_experiment_service import AIExperimentService

            settings = get_settings()
            engine = create_async_engine(settings.DATABASE_URL, echo=False)
            async with AsyncSession(engine) as db:
                service = AIExperimentService(db)
                result = await service.run_experiment(
                    _UUID(experiment_id), _UUID(user_id)
                )
                return result.model_dump() if result else None

        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(_run())
        finally:
            loop.close()

        logger.info(
            "ab_experiment_completed",
            experiment_id=experiment_id,
            status=result.get("status") if result else "not_found",
        )
        return result

    except Exception as exc:
        logger.error(
            "ab_experiment_failed", experiment_id=experiment_id, error=str(exc)
        )
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=1, default_retry_delay=300)
def calculate_performance_metrics(self):
    """Haftalık AI performans metrikleri hesaplama.

    ai_analysis_logs tablosundaki kayıtları tarar,
    gerçek fiyat hareketleri ile karşılaştırır ve is_correct alanını günceller.
    """
    try:

        async def _calculate():
            from sqlalchemy import text, update
            from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

            from app.config import get_settings
            from app.models.ai import AIAnalysisLog

            settings = get_settings()
            engine = create_async_engine(settings.DATABASE_URL, echo=False)
            async with AsyncSession(engine) as db:
                # 1. Henüz değerlendirilmemiş logları bul
                #    Son 7 gün içindeki, is_correct=NULL olanlar
                result = await db.execute(
                    text("""
                        UPDATE ai_analysis_logs AS cal
                        SET
                            actual_price_change = sub.price_change,
                            is_correct = CASE
                                WHEN cal.action = 'buy' AND sub.price_change > 0 THEN TRUE
                                WHEN cal.action = 'sell' AND sub.price_change < 0 THEN TRUE
                                WHEN cal.action = 'hold' AND ABS(sub.price_change) < 2.0 THEN TRUE
                                ELSE FALSE
                            END
                        FROM (
                            SELECT
                                cal2.id AS log_id,
                                COALESCE(
                                    ((latest.close - first.close) / NULLIF(first.close, 0)) * 100,
                                    0
                                ) AS price_change
                            FROM ai_analysis_logs cal2
                            JOIN symbols s ON s.ticker = cal2.symbol
                            LEFT JOIN LATERAL (
                                SELECT close FROM ohlcv_data
                                WHERE symbol_id = s.id AND time >= cal2.created_at
                                ORDER BY time ASC LIMIT 1
                            ) first ON TRUE
                            LEFT JOIN LATERAL (
                                SELECT close FROM ohlcv_data
                                WHERE symbol_id = s.id AND time >= cal2.created_at + INTERVAL '3 days'
                                ORDER BY time ASC LIMIT 1
                            ) latest ON TRUE
                            WHERE cal2.is_correct IS NULL
                                AND cal2.created_at < NOW() - INTERVAL '3 days'
                        ) sub
                        WHERE cal.id = sub.log_id
                    """)
                )
                updated = result.rowcount
                await db.commit()

                logger.info(
                    "performance_metrics_calculated", updated_logs=updated
                )
                return {"updated_logs": updated}

        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(_calculate())
        finally:
            loop.close()

        return result

    except Exception as exc:
        logger.error("performance_metrics_failed", error=str(exc))
        raise self.retry(exc=exc)
