# Source: Doc 07 §12.2 pattern — User Repository
"""Kullanıcı veri erişim katmanı."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """User modeli için özelleştirilmiş repository."""

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> User | None:
        """E-posta adresine göre kullanıcı getirir."""
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: UUID) -> User | None:
        """ID'ye göre kullanıcı getirir."""
        return await self.db.get(User, user_id)

    async def get_active_users(self, skip: int = 0, limit: int = 20) -> list[User]:
        """Aktif kullanıcıları listeler."""
        stmt = (
            select(User)
            .where(User.is_active.is_(True))
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_last_login(self, user: User) -> User:
        """Son giriş zamanını günceller."""
        from datetime import datetime, timezone

        user.last_login_at = datetime.now(timezone.utc)
        await self.db.flush()
        return user

    async def deactivate(self, user: User) -> User:
        """Kullanıcıyı deaktif eder."""
        user.is_active = False
        await self.db.flush()
        return user

    async def verify(self, user: User) -> User:
        """Kullanıcıyı doğrulanmış olarak işaretler."""
        user.is_verified = True
        await self.db.flush()
        return user

    async def email_exists(self, email: str) -> bool:
        """E-posta adresinin kullanılıp kullanılmadığını kontrol eder."""
        user = await self.get_by_email(email)
        return user is not None
