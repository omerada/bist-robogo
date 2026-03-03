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

    async def _run():
        from app.database import async_session_factory
        from app.services.market_data_service import MarketDataService

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


@celery_app.task(bind=True, max_retries=3, default_retry_delay=120)
def update_index_components(self):
    """Haftalık endeks bileşen güncelleme."""
    logger.info("index_components_update_started")
    # TODO: Implement index component update logic
    return {"status": "not_implemented"}
