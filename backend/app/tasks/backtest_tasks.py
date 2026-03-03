# Source: Doc 07 §20 pattern — Backtest Celery tasks
"""Backtest Celery görevleri — asenkron backtest çalıştırma."""

import structlog

from app.tasks.celery_app import celery_app

logger = structlog.get_logger()


@celery_app.task(
    bind=True,
    max_retries=1,
    default_retry_delay=30,
    soft_time_limit=1800,
    time_limit=2400,
)
def run_backtest_async(self, backtest_id: str):
    """Backtest'i asenkron olarak çalıştır.

    API endpoint kısa süreli senkron çalışma yapar.
    Büyük veri setleri veya çoklu sembol için bu Celery task kullanılır.
    """
    import asyncio

    async def _run():
        from uuid import UUID

        from app.database import async_session_factory
        from app.services.backtest_service import BacktestService

        async with async_session_factory() as db:
            service = BacktestService(db)
            result = await service.run_backtest(UUID(backtest_id))
            logger.info(
                "backtest_completed",
                backtest_id=backtest_id,
                status=result.status,
                total_trades=result.total_trades,
                total_return=str(result.total_return),
            )
            return {
                "backtest_id": backtest_id,
                "status": result.status,
                "total_trades": result.total_trades,
            }

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error(
            "backtest_task_failed",
            backtest_id=backtest_id,
            error=str(exc),
        )
        raise self.retry(exc=exc)
