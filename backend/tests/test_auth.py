# Source: Doc 07 §24 (test) — Auth endpoint testleri
"""Kimlik doğrulama endpoint testleri."""

import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_register_success(client):
    """POST /api/v1/auth/register → 201 Created."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "Test1234!",
            "full_name": "New User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == "newuser@example.com"
    assert data["data"]["full_name"] == "New User"
    assert data["data"]["role"] == "trader"
    assert "password_hash" not in data["data"]


async def test_register_duplicate_email(client):
    """POST /api/v1/auth/register — aynı e-posta → 409 Conflict."""
    # İlk kayıt
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "Test1234!",
            "full_name": "First User",
        },
    )
    # Aynı e-posta ile tekrar
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "Test1234!",
            "full_name": "Second User",
        },
    )
    assert response.status_code == 409


async def test_register_invalid_email(client):
    """POST /api/v1/auth/register — geçersiz e-posta → 422."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "password": "Test1234!",
            "full_name": "Bad Email User",
        },
    )
    assert response.status_code == 422


async def test_register_short_password(client):
    """POST /api/v1/auth/register — kısa şifre → 422."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "shortpw@example.com",
            "password": "123",
            "full_name": "Short Password",
        },
    )
    assert response.status_code == 422


async def test_login_success(client):
    """POST /api/v1/auth/login → 200 + token."""
    # Önce kayıt ol
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "loginuser@example.com",
            "password": "Test1234!",
            "full_name": "Login User",
        },
    )
    # Giriş yap
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "loginuser@example.com",
            "password": "Test1234!",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"
    assert data["data"]["expires_in"] > 0


async def test_login_wrong_password(client):
    """POST /api/v1/auth/login — yanlış şifre → 401."""
    # Önce kayıt ol
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrongpw@example.com",
            "password": "Test1234!",
            "full_name": "Wrong PW User",
        },
    )
    # Yanlış şifre ile giriş
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrongpw@example.com",
            "password": "WrongPassword1!",
        },
    )
    assert response.status_code == 401


async def test_login_nonexistent_user(client):
    """POST /api/v1/auth/login — kayıtlı olmayan kullanıcı → 401."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "Test1234!",
        },
    )
    assert response.status_code == 401


async def test_me_authenticated(auth_client, test_user):
    """GET /api/v1/auth/me → 200 + kullanıcı bilgisi."""
    response = await auth_client.get("/api/v1/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == test_user.email
    assert data["data"]["full_name"] == test_user.full_name


async def test_me_unauthenticated(client):
    """GET /api/v1/auth/me — token yok → 403."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 403


async def test_logout(auth_client):
    """POST /api/v1/auth/logout → 200."""
    response = await auth_client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
