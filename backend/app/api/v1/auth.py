# Source: Doc 07 §10.3 — Auth Router
"""Kimlik doğrulama endpoint'leri."""

from fastapi import APIRouter, Cookie, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    Enable2FAResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
    Verify2FARequest,
)
from app.schemas.common import APIResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=APIResponse[UserResponse], status_code=201)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Yeni kullanıcı kaydı."""
    service = AuthService(db)
    user = await service.register(body)
    return APIResponse(success=True, data=UserResponse.model_validate(user))


@router.post("/login", response_model=APIResponse[TokenResponse])
async def login(
    body: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Kullanıcı girişi."""
    service = AuthService(db)
    tokens = await service.login(body)

    # Refresh token'ı httpOnly cookie olarak set et
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
        path="/api/v1/auth",
    )

    return APIResponse(success=True, data=tokens)


@router.post("/refresh", response_model=APIResponse[TokenResponse])
async def refresh_token(
    response: Response,
    db: AsyncSession = Depends(get_db),
    refresh_token: str | None = Cookie(None),
):
    """Access token yenileme (refresh token ile)."""
    service = AuthService(db)
    tokens = await service.refresh(refresh_token)

    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
        path="/api/v1/auth",
    )

    return APIResponse(success=True, data=tokens)


@router.post("/logout")
async def logout(
    response: Response,
    user: User = Depends(get_current_user),
):
    """Oturum kapatma — refresh token cookie'sini siler."""
    response.delete_cookie("refresh_token", path="/api/v1/auth")
    return APIResponse(success=True, data={"message": "Oturum kapatıldı"})


@router.get("/me", response_model=APIResponse[UserResponse])
async def get_me(user: User = Depends(get_current_user)):
    """Mevcut kullanıcı bilgilerini döner."""
    return APIResponse(success=True, data=UserResponse.model_validate(user))


@router.post("/2fa/enable", response_model=APIResponse[Enable2FAResponse])
async def enable_2fa(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """2FA etkinleştirme."""
    service = AuthService(db)
    result = await service.enable_2fa(user)
    return APIResponse(success=True, data=result)


@router.post("/2fa/verify")
async def verify_2fa(
    body: Verify2FARequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """2FA doğrulama."""
    service = AuthService(db)
    await service.verify_2fa(user, body.code)
    return APIResponse(success=True, data={"message": "2FA doğrulandı"})
