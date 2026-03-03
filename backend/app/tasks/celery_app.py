"""Celery uygulama yapılandırması."""

from celery import Celery
from celery.schedules import crontab

from app.config import get_settings

settings = get_settings()

# Doc 11 tutarsızlık #5: Ayrı CELERY_BROKER_URL ve CELERY_RESULT_BACKEND env var'ları kullan
celery_app = Celery(
    "bist_robogo",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
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
