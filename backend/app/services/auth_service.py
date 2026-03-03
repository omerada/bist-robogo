"""Kimlik doğrulama servisi — kayıt, giriş, token yönetimi, 2FA."""

from datetime import timedelta
from uuid import uuid4

import pyotp
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.exceptions import (
    ConflictException,
    NotFoundException,
    UnauthorizedException,
)
from app.models.user import User
from app.schemas.auth import (
    Enable2FAResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)

logger = structlog.get_logger()
settings = get_settings()


class AuthService:
    """Kullanıcı kimlik doğrulama iş mantığı."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, data: RegisterRequest) -> User:
        """Yeni kullanıcı kaydı oluşturur.

        Raises:
            ConflictException: E-posta zaten kullanılıyorsa.
        """
        # E-posta kontrolü
        stmt = select(User).where(User.email == data.email)
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            raise ConflictException("Bu e-posta adresi zaten kullanılıyor")

        user = User(
            id=uuid4(),
            email=data.email,
            password_hash=hash_password(data.password),
            full_name=data.full_name,
            role="trader",
            is_active=True,
            is_verified=False,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        logger.info("user_registered", user_id=str(user.id), email=user.email)
        return user

    async def login(self, data: LoginRequest) -> TokenResponse:
        """Kullanıcı girişi yapar ve token üretir.

        Raises:
            UnauthorizedException: E-posta veya şifre hatalıysa.
        """
        stmt = select(User).where(User.email == data.email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not verify_password(data.password, user.password_hash):
            raise UnauthorizedException("Geçersiz e-posta veya şifre")

        if not user.is_active:
            raise UnauthorizedException("Hesap devre dışı")

        # 2FA kontrolü
        if user.two_factor_enabled and not data.totp_code:
            raise UnauthorizedException("2FA kodu gerekli", detail="2fa_required")

        if user.two_factor_enabled and data.totp_code:
            if not self._verify_totp(user.two_factor_secret, data.totp_code):
                raise UnauthorizedException("Geçersiz 2FA kodu")

        access_token = create_access_token(user.id, user.role)
        refresh_token = create_refresh_token(user.id)

        logger.info("user_logged_in", user_id=str(user.id))

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def refresh(self, refresh_token: str | None) -> TokenResponse:
        """Refresh token ile yeni access token üretir.

        Raises:
            UnauthorizedException: Refresh token geçersizse.
        """
        if not refresh_token:
            raise UnauthorizedException("Refresh token bulunamadı")

        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedException("Geçersiz refresh token")

        user_id = payload.get("sub")
        user = await self.db.get(User, user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("Kullanıcı bulunamadı veya devre dışı")

        access_token = create_access_token(user.id, user.role)
        new_refresh_token = create_refresh_token(user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def enable_2fa(self, user: User) -> Enable2FAResponse:
        """2FA etkinleştirme — TOTP secret ve QR URI üretir."""
        secret = pyotp.random_base32()
        user.two_factor_secret = secret
        await self.db.commit()

        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user.email,
            issuer_name=settings.APP_NAME,
        )

        logger.info("2fa_enabled", user_id=str(user.id))

        return Enable2FAResponse(
            secret=secret,
            qr_uri=provisioning_uri,
        )

    async def verify_2fa(self, user: User, code: str) -> None:
        """2FA doğrulama kodu kontrol eder.

        Raises:
            UnauthorizedException: Kod geçersizse.
        """
        if not user.two_factor_secret:
            raise NotFoundException("2FA", "etkinleştirilmemiş")

        if not self._verify_totp(user.two_factor_secret, code):
            raise UnauthorizedException("Geçersiz 2FA kodu")

        user.two_factor_enabled = True
        await self.db.commit()

        logger.info("2fa_verified", user_id=str(user.id))

    @staticmethod
    def _verify_totp(secret: str, code: str) -> bool:
        """TOTP kodunu doğrular (±1 pencere toleransı)."""
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)
