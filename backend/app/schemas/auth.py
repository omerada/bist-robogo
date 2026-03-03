# Source: Doc 07 §11.2 — Kimlik doğrulama şemaları
"""Kimlik doğrulama şemaları."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128, description="Min 8 karakter, 1 büyük harf, 1 rakam")
    full_name: str = Field(..., min_length=2, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    totp_code: str | None = Field(None, min_length=6, max_length=6, description="2FA aktifse gerekli")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # saniye
    refresh_token: str


class TokenPayload(BaseModel):
    sub: str
    role: str
    exp: int
    type: str


class Enable2FAResponse(BaseModel):
    secret: str
    qr_code_uri: str


class Verify2FARequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=6)


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    two_factor_enabled: bool
    last_login_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
