"""Pytest fixture'ları — test DB, factory'ler, authenticated client."""

import os
from uuid import uuid4

import pytest
import pytest_asyncio

# Tüm testlerin session-scoped event loop'ta çalışmasını sağla.
# Fixtures zaten loop_scope="session" kullanıyor; testler de aynı loop'ta olmalı,
# aksi halde asyncpg "Future attached to a different loop" hatası verir.
pytestmark = pytest.mark.asyncio(loop_scope="session")
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.security import create_access_token, hash_password
from app.database import Base, get_db
from app.main import create_app
from app.models.user import User

# Test DB URL — env variable veya Docker default
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://bist_user:bist_dev_pass_2026@localhost:5432/bist_robogo_test",
)


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def engine():
    eng = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture(loop_scope="session")
async def db(engine):
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(loop_scope="session")
async def app(db):
    application = create_app()

    async def override_get_db():
        yield db

    application.dependency_overrides[get_db] = override_get_db
    return application


@pytest_asyncio.fixture(loop_scope="session")
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(loop_scope="session")
async def test_user(db) -> User:
    """Test kullanıcısı oluştur (idempotent)."""
    from sqlalchemy import select

    result = await db.execute(select(User).where(User.email == "test@example.com"))
    user = result.scalar_one_or_none()
    if user:
        return user

    user = User(
        id=uuid4(),
        email="test@example.com",
        password_hash=hash_password("Test1234!"),
        full_name="Test User",
        role="trader",
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    await db.flush()
    return user


@pytest_asyncio.fixture(loop_scope="session")
async def auth_client(client, test_user) -> AsyncClient:
    """Authenticated test client."""
    token = create_access_token(test_user.id, test_user.role)
    client.headers["Authorization"] = f"Bearer {token}"
    return client
