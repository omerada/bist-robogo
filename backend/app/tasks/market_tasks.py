"""Piyasa verisi Celery görevleri."""

from app.tasks.celery_app import celery_app
import structlog

logger = structlog.get_logger()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_eod_data(self):
    """Günlük kapanış (EOD) verilerini tüm semboller için çek ve kaydet.

    Adımlar:
    1. Aktif sembolleri DB'den al
    2. CollectAPI üzerinden güncel fiyatları çek
    3. Redis cache güncelle
    4. Başarı/hata logla
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


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def fetch_live_prices(self):
    """CollectAPI üzerinden canlı fiyatları çeker ve Redis cache'e yazar.

    Piyasa saatleri içinde (10:00 - 18:00) çalışır.
    Celery beat ile her 1 dakikada tetiklenir.
    """
    import asyncio
    import json
    from datetime import datetime, timezone

    async def _run():
        from app.config import get_settings
        from app.core.collectapi_client import CollectAPIClient
        from app.core.redis_client import redis_manager

        settings = get_settings()

        # Piyasa saatlerini kontrol et
        now_utc = datetime.now(timezone.utc)
        # Türkiye UTC+3
        turkey_hour = (now_utc.hour + 3) % 24
        if turkey_hour < settings.MARKET_OPEN_HOUR or turkey_hour >= settings.MARKET_CLOSE_HOUR:
            logger.info("market_closed", turkey_hour=turkey_hour)
            return {"status": "market_closed", "updated": 0}

        # CollectAPI API key kontrolü
        if not settings.COLLECTAPI_KEY:
            logger.warning("collectapi_key_missing")
            return {"status": "no_api_key", "updated": 0}

        client = CollectAPIClient()
        try:
            stocks = await client.get_all_stocks()
            if not stocks:
                logger.warning("collectapi_no_data")
                return {"status": "no_data", "updated": 0}

            updated = 0
            for stock in stocks:
                code = stock.get("code", "").upper()
                if not code:
                    continue

                parsed = CollectAPIClient.parse_stock_to_quote(stock)
                cache_key = f"market:quote:{code}"
                cache_data = json.dumps({
                    "price": parsed["price"],
                    "bid": parsed["price"] * 0.999,
                    "ask": parsed["price"] * 1.001,
                    "volume": parsed["volume"],
                    "change_pct": parsed["change_pct"],
                    "name": parsed["name"],
                    "source": "collectapi",
                    "updated_at": now_utc.isoformat(),
                })
                await redis_manager.set_cached(
                    cache_key, cache_data, ttl=settings.COLLECTAPI_CACHE_TTL,
                )
                updated += 1

            logger.info("live_prices_updated", count=updated)
            return {"status": "ok", "updated": updated}

        finally:
            await client.close()

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("live_prices_fetch_failed", error=str(exc))
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60)
def fetch_indices(self):
    """CollectAPI üzerinden BIST endeks verilerini çeker ve Redis cache'e yazar."""
    import asyncio
    import json
    from datetime import datetime, timezone

    async def _run():
        from app.config import get_settings
        from app.core.collectapi_client import CollectAPIClient
        from app.core.redis_client import redis_manager

        settings = get_settings()
        if not settings.COLLECTAPI_KEY:
            return {"status": "no_api_key", "updated": 0}

        client = CollectAPIClient()
        try:
            indices = await client.get_indices()
            now_utc = datetime.now(timezone.utc)
            updated = 0

            for idx in indices:
                code = idx.get("code", "").upper()
                if not code:
                    continue

                cache_key = f"market:index:{code}"
                cache_data = json.dumps({
                    "name": idx.get("name", ""),
                    "price": idx.get("lastprice", "0"),
                    "rate": idx.get("rate", "0"),
                    "source": "collectapi",
                    "updated_at": now_utc.isoformat(),
                })
                await redis_manager.set_cached(cache_key, cache_data, ttl=300)
                updated += 1

            logger.info("indices_updated", count=updated)
            return {"status": "ok", "updated": updated}
        finally:
            await client.close()

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("indices_fetch_failed", error=str(exc))
        raise self.retry(exc=exc)
