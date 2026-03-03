"""Notification API testleri — Sprint 2.3."""

import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")


class TestNotificationAPI:
    """Bildirim endpoint testleri."""

    # ── GET /api/v1/notifications/ ──

    async def test_list_notifications_unauthenticated(self, client):
        """Auth olmadan → 403."""
        resp = await client.get("/api/v1/notifications/")
        assert resp.status_code == 403

    async def test_list_notifications_empty(self, auth_client):
        """Boş bildirim listesi."""
        resp = await auth_client.get("/api/v1/notifications/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert data["meta"]["total"] >= 0

    # ── GET /api/v1/notifications/unread-count ──

    async def test_unread_count_unauthenticated(self, client):
        """Auth olmadan → 403."""
        resp = await client.get("/api/v1/notifications/unread-count")
        assert resp.status_code == 403

    async def test_unread_count_initial(self, auth_client):
        """Başlangıçta okunmamış sayısı ≥ 0."""
        resp = await auth_client.get("/api/v1/notifications/unread-count")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert isinstance(data["data"]["count"], int)

    # ── Bildirim oluşturma + CRUD akışı ──

    async def test_create_and_list_notification(self, auth_client, db, test_user):
        """DB üzerinden bildirim oluştur, API ile listele."""
        from app.services.notification_service import NotificationService

        service = NotificationService(db)
        await service.create_notification(
            user_id=test_user.id,
            type="info",
            title="Test Bildirim",
            body="Sprint 2.3 test bildirimi",
            channel="in_app",
        )

        resp = await auth_client.get("/api/v1/notifications/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        notifications = data["data"]
        assert any(n["title"] == "Test Bildirim" for n in notifications)

    async def test_unread_count_after_create(self, auth_client):
        """Bildirim oluşturduktan sonra okunmamış sayısı artmalı."""
        resp = await auth_client.get("/api/v1/notifications/unread-count")
        assert resp.status_code == 200
        assert resp.json()["data"]["count"] >= 1

    # ── PUT /api/v1/notifications/{id}/read ──

    async def test_mark_read_unauthenticated(self, client):
        """Auth olmadan → 403."""
        resp = await client.put(
            "/api/v1/notifications/00000000-0000-0000-0000-000000000000/read"
        )
        assert resp.status_code == 403

    async def test_mark_read_not_found(self, auth_client):
        """Olmayan bildirim → 404."""
        resp = await auth_client.put(
            "/api/v1/notifications/00000000-0000-0000-0000-000000000000/read"
        )
        assert resp.status_code == 404

    async def test_mark_read_success(self, auth_client):
        """Bildirimi okundu olarak işaretle."""
        # Önce listele
        list_resp = await auth_client.get("/api/v1/notifications/?is_read=false")
        notifications = list_resp.json()["data"]
        if not notifications:
            pytest.skip("Okunmamış bildirim yok")
        notif_id = notifications[0]["id"]

        # Okundu yap
        resp = await auth_client.put(f"/api/v1/notifications/{notif_id}/read")
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    # ── PUT /api/v1/notifications/read-all ──

    async def test_mark_all_read_unauthenticated(self, client):
        """Auth olmadan → 403."""
        resp = await client.put("/api/v1/notifications/read-all")
        assert resp.status_code == 403

    async def test_mark_all_read_success(self, auth_client, db, test_user):
        """Tüm bildirimler okundu."""
        # Önce birkaç bildirim oluştur
        from app.services.notification_service import NotificationService

        service = NotificationService(db)
        for i in range(3):
            await service.create_notification(
                user_id=test_user.id,
                type="info",
                title=f"Toplu Test {i}",
                body=f"Toplu okundu testi #{i}",
                channel="in_app",
            )

        resp = await auth_client.put("/api/v1/notifications/read-all")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert isinstance(data["data"]["updated"], int)

        # Unread sayısı 0 olmalı
        count_resp = await auth_client.get("/api/v1/notifications/unread-count")
        assert count_resp.json()["data"]["count"] == 0

    # ── DELETE /api/v1/notifications/{id} ──

    async def test_delete_notification_unauthenticated(self, client):
        """Auth olmadan → 403."""
        resp = await client.delete(
            "/api/v1/notifications/00000000-0000-0000-0000-000000000000"
        )
        assert resp.status_code == 403

    async def test_delete_notification_not_found(self, auth_client):
        """Olmayan bildirim → 404."""
        resp = await auth_client.delete(
            "/api/v1/notifications/00000000-0000-0000-0000-000000000000"
        )
        assert resp.status_code == 404

    async def test_delete_notification_success(self, auth_client, db, test_user):
        """Bildirim oluştur ve sil."""
        from app.services.notification_service import NotificationService

        service = NotificationService(db)
        notif = await service.create_notification(
            user_id=test_user.id,
            type="warning",
            title="Silinecek Bildirim",
            body="Bu bildirim silinecek",
            channel="in_app",
        )

        resp = await auth_client.delete(f"/api/v1/notifications/{notif.id}")
        assert resp.status_code == 200
        assert resp.json()["success"] is True

        # Tekrar silme → 404
        resp2 = await auth_client.delete(f"/api/v1/notifications/{notif.id}")
        assert resp2.status_code == 404

    # ── Filtreleme ──

    async def test_list_filter_by_read_status(self, auth_client):
        """is_read filtresi çalışmalı."""
        resp = await auth_client.get("/api/v1/notifications/?is_read=true")
        assert resp.status_code == 200
        data = resp.json()
        for n in data["data"]:
            assert n["is_read"] is True

    async def test_list_filter_by_channel(self, auth_client):
        """channel filtresi çalışmalı."""
        resp = await auth_client.get("/api/v1/notifications/?channel=in_app")
        assert resp.status_code == 200
        data = resp.json()
        for n in data["data"]:
            assert n["channel"] == "in_app"

    async def test_list_pagination(self, auth_client):
        """Sayfalama parametreleri."""
        resp = await auth_client.get("/api/v1/notifications/?page=1&per_page=5")
        assert resp.status_code == 200
        data = resp.json()
        assert data["meta"]["page"] == 1
        assert data["meta"]["per_page"] == 5

    # ── Bildirim alanları ──

    async def test_notification_fields(self, auth_client, db, test_user):
        """Bildirim yanıtında tüm gerekli alanlar olmalı."""
        from app.services.notification_service import NotificationService

        service = NotificationService(db)
        await service.create_notification(
            user_id=test_user.id,
            type="risk_alert",
            title="Alan Testi",
            body="Tüm alanlar mevcut olmalı",
            channel="in_app",
            metadata={"severity": "high"},
        )

        resp = await auth_client.get("/api/v1/notifications/")
        notifications = resp.json()["data"]
        test_notif = next(
            (n for n in notifications if n["title"] == "Alan Testi"), None
        )
        assert test_notif is not None
        assert "id" in test_notif
        assert "user_id" in test_notif
        assert "type" in test_notif
        assert "title" in test_notif
        assert "body" in test_notif
        assert "channel" in test_notif
        assert "is_read" in test_notif
        assert "sent_at" in test_notif
