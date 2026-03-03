# Source: Doc 10 §celery_app beat_schedule — Bakım görevleri
"""Veritabanı bakım ve portföy snapshot Celery görevleri."""

import asyncio
import logging

import structlog

from app.tasks.celery_app import celery_app

logger = structlog.get_logger()


@celery_app.task(bind=True, max_retries=1, default_retry_delay=300)
def take_portfolio_snapshots(self):
    """Günlük portföy snapshot'ı — tüm aktif kullanıcılar için.

    Her gün BIST kapanış sonrası (18:00) çalışır.
    Portföy değerini, pozisyon dağılımını ve equity değerini kaydeder.
    """
    try:

        async def _snapshot():
            from sqlalchemy import text
            from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

            from app.config import get_settings

            settings = get_settings()
            engine = create_async_engine(settings.DATABASE_URL, echo=False)

            async with AsyncSession(engine) as db:
                # Aktif portföylerin snapshot'ını al
                result = await db.execute(
                    text("""
                        INSERT INTO portfolio_snapshots (id, portfolio_id, total_value, cash_balance, invested_value, daily_pnl, snapshot_date)
                        SELECT
                            gen_random_uuid(),
                            p.id,
                            p.total_value,
                            p.cash_balance,
                            p.invested_value,
                            COALESCE(p.total_value - LAG(ps.total_value) OVER (PARTITION BY p.id ORDER BY ps.snapshot_date), 0),
                            CURRENT_DATE
                        FROM portfolios p
                        LEFT JOIN LATERAL (
                            SELECT total_value, snapshot_date
                            FROM portfolio_snapshots ps2
                            WHERE ps2.portfolio_id = p.id
                            ORDER BY ps2.snapshot_date DESC
                            LIMIT 1
                        ) ps ON true
                        WHERE NOT EXISTS (
                            SELECT 1 FROM portfolio_snapshots ps3
                            WHERE ps3.portfolio_id = p.id AND ps3.snapshot_date = CURRENT_DATE
                        )
                    """)
                )
                await db.commit()
                return result.rowcount

        loop = asyncio.new_event_loop()
        try:
            count = loop.run_until_complete(_snapshot())
        finally:
            loop.close()

        logger.info("portfolio_snapshots_completed", count=count)
        return {"status": "ok", "snapshots": count}

    except Exception as exc:
        logger.error("portfolio_snapshots_failed", error=str(exc))
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=1, default_retry_delay=600)
def database_maintenance(self):
    """Haftalık veritabanı bakım görevi — Pazar gece 03:00.

    - VACUUM ANALYZE (tablo istatistikleri güncelle)
    - Eski audit log'larını temizle (90 gün+)
    - Eski bildirim kayıtlarını temizle (60 gün+, okunmuş olanlar)
    """
    try:

        async def _maintain():
            from sqlalchemy import text
            from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

            from app.config import get_settings

            settings = get_settings()
            engine = create_async_engine(
                settings.DATABASE_URL, echo=False, isolation_level="AUTOCOMMIT"
            )

            results = {}

            async with AsyncSession(engine) as db:
                # 1. Eski audit log temizliği (90 gün+)
                r1 = await db.execute(
                    text(
                        "DELETE FROM audit_logs WHERE created_at < NOW() - INTERVAL '90 days'"
                    )
                )
                results["audit_logs_cleaned"] = r1.rowcount

                # 2. Eski okunmuş bildirim temizliği (60 gün+)
                r2 = await db.execute(
                    text(
                        "DELETE FROM notifications WHERE is_read = true AND created_at < NOW() - INTERVAL '60 days'"
                    )
                )
                results["notifications_cleaned"] = r2.rowcount

            # 3. VACUUM ANALYZE (AUTOCOMMIT modunda çalışmalı)
            async with engine.connect() as conn:
                await conn.execute(text("VACUUM ANALYZE"))
                results["vacuum"] = "completed"

            return results

        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(_maintain())
        finally:
            loop.close()

        logger.info("database_maintenance_completed", **result)
        return result

    except Exception as exc:
        logger.error("database_maintenance_failed", error=str(exc))
        raise self.retry(exc=exc)
