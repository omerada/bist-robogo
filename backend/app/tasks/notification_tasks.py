"""Bildirim Celery görevleri — Email (SMTP) + Telegram."""

import asyncio
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import structlog

from app.config import get_settings
from app.tasks.celery_app import celery_app

logger = structlog.get_logger()
settings = get_settings()


# ── Email Gönderim ──


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def send_email_notification(self, to_email: str, subject: str, body_html: str):
    """SMTP ile email gönder."""
    try:
        if not settings.SMTP_HOST or not settings.SMTP_USER:
            logger.warning("email_skipped", reason="SMTP yapılandırma eksik")
            return {"status": "skipped", "reason": "SMTP not configured"}

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM_EMAIL
        msg["To"] = to_email
        msg.attach(MIMEText(body_html, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD.get_secret_value())
            server.send_message(msg)

        logger.info("email_sent", to=to_email, subject=subject)
        return {"status": "sent", "to": to_email}

    except Exception as exc:
        logger.error("email_send_failed", to=to_email, error=str(exc))
        raise self.retry(exc=exc)


# ── Telegram Gönderim ──


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def send_telegram_notification(self, chat_id: str | None, message: str):
    """Telegram bot ile mesaj gönder."""
    try:
        token = settings.TELEGRAM_BOT_TOKEN
        target_chat = chat_id or settings.TELEGRAM_DEFAULT_CHAT_ID

        if not token or not target_chat:
            logger.warning("telegram_skipped", reason="Telegram yapılandırma eksik")
            return {"status": "skipped", "reason": "Telegram not configured"}

        import urllib.request
        import json

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = json.dumps({
            "chat_id": target_chat,
            "text": message,
            "parse_mode": "HTML",
        }).encode("utf-8")

        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())

        logger.info("telegram_sent", chat_id=target_chat)
        return {"status": "sent", "chat_id": target_chat, "ok": result.get("ok")}

    except Exception as exc:
        logger.error("telegram_send_failed", error=str(exc))
        raise self.retry(exc=exc)


# ── Günlük Risk Raporu ──


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60)
def send_daily_risk_report(self):
    """Tüm aktif kullanıcılara günlük risk özeti gönder."""

    async def _run():
        from app.database import async_session_factory
        from app.models.user import User
        from app.services.risk_service import RiskService
        from sqlalchemy import select

        async with async_session_factory() as db:
            # Aktif kullanıcıları al
            result = await db.execute(
                select(User).where(User.is_active == True)  # noqa: E712
            )
            users = list(result.scalars().all())

            for user in users:
                try:
                    service = RiskService(db)
                    status = await service.get_status(user.id)

                    # In-app bildirim oluştur
                    from app.services.notification_service import NotificationService
                    notif_service = NotificationService(db)
                    await notif_service.create_notification(
                        user_id=user.id,
                        type="risk_report",
                        title="Günlük Risk Raporu",
                        body=(
                            f"Risk Seviyesi: {status.overall_risk.value.upper()} | "
                            f"Günlük Kayıp: ₺{status.daily_loss:,.0f} / ₺{status.daily_loss_limit:,.0f} | "
                            f"Açık Pozisyon: {status.open_positions}/{status.max_positions} | "
                            f"Aktif Kural: {status.rules_active}"
                        ),
                        channel="in_app",
                        metadata={"risk_level": status.overall_risk.value},
                    )
                except Exception as e:
                    logger.error("risk_report_user_error", user_id=str(user.id), error=str(e))

            logger.info("daily_risk_report_completed", user_count=len(users))
            return {"status": "completed", "users": len(users)}

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("daily_risk_report_failed", error=str(exc))
        raise self.retry(exc=exc)


# ── Genel Bildirim Gönderim ──


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def send_notification(self, user_id: str, type: str, title: str, body: str, channels: list[str] | None = None):
    """Çoklu kanala bildirim gönder. channels: ["in_app", "email", "telegram"]"""
    channels = channels or ["in_app"]

    async def _run():
        from app.database import async_session_factory
        from app.models.user import User
        from app.services.notification_service import NotificationService
        from uuid import UUID

        async with async_session_factory() as db:
            uid = UUID(user_id)
            user = await db.get(User, uid)
            if not user:
                logger.warning("notification_user_not_found", user_id=user_id)
                return {"status": "user_not_found"}

            # In-app her zaman
            if "in_app" in channels:
                service = NotificationService(db)
                await service.create_notification(
                    user_id=uid, type=type, title=title, body=body,
                    channel="in_app",
                )

            # Email
            if "email" in channels and user.email:
                send_email_notification.delay(
                    to_email=user.email,
                    subject=f"[BIST Robogo] {title}",
                    body_html=f"<h3>{title}</h3><p>{body}</p>",
                )

            # Telegram
            if "telegram" in channels:
                send_telegram_notification.delay(
                    chat_id=None,
                    message=f"<b>{title}</b>\n{body}",
                )

            return {"status": "dispatched", "channels": channels}

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("notification_dispatch_failed", error=str(exc))
        raise self.retry(exc=exc)
