# Source: Doc 10 §Faz 3 Sprint 3.1 — AI API endpoint'leri
"""AI analiz, sohbet ve sinyal endpoint'leri."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.ai import (
    AIAnalysisRequest,
    AIChatRequest,
    AISettingsRequest,
)
from app.schemas.common import APIResponse
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze")
async def analyze_symbol(
    request: AIAnalysisRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Bir sembol için AI tabanlı teknik analiz yap.

    - Teknik göstergeleri hesaplar
    - OpenRouter LLM'e gönderir
    - Yapılandırılmış analiz yanıtı döner
    """
    service = AIService(db)
    analysis = await service.analyze_symbol(
        symbol=request.symbol.upper(),
        period=request.period,
        include_indicators=request.include_indicators,
    )
    return APIResponse(success=True, data=analysis.model_dump())


@router.post("/chat")
async def ai_chat(
    request: AIChatRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """AI sohbet — piyasa, hisse, strateji hakkında soru-cevap.

    Mesaj geçmişi ile bağlamsal yanıt üretir.
    """
    service = AIService(db)
    response = await service.chat(
        messages=request.messages,
        symbol=request.symbol,
    )
    return APIResponse(success=True, data=response.model_dump())


@router.get("/signals")
async def get_ai_signals(
    limit: int = 10,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """AI tabanlı alım/satım sinyalleri üret.

    Aktif BIST sembollerini analiz edip en güçlü sinyalleri döner.
    """
    service = AIService(db)
    signals = await service.generate_signals(limit=limit)
    return APIResponse(success=True, data=signals.model_dump())


@router.get("/models")
async def list_models(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Kullanılabilir OpenRouter modellerini listele."""
    service = AIService(db)
    models = await service.list_models()
    return APIResponse(success=True, data=models.model_dump())


@router.get("/settings")
async def get_ai_settings(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mevcut AI ayarlarını getir."""
    service = AIService(db)
    settings = service.get_settings()
    return APIResponse(success=True, data=settings.model_dump())


@router.put("/settings")
async def update_ai_settings(
    request: AISettingsRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """AI ayarlarını güncelle (model, temperature, max_tokens).

    Not: Bu ayarlar şimdilik session-level'da uygulanır.
    Kalıcı ayarlar Sprint 3.3'te user_settings tablosuna eklenecek.
    """
    from app.core.openrouter_client import OpenRouterClient

    # Basit validation: model ID boş olamaz
    if request.model is not None and not request.model.strip():
        raise HTTPException(status_code=400, detail="Model ID boş olamaz")

    # Ayarları oluştur
    kwargs = {}
    if request.model:
        kwargs["model"] = request.model
    if request.temperature is not None:
        kwargs["temperature"] = request.temperature
    if request.max_tokens is not None:
        kwargs["max_tokens"] = request.max_tokens

    client = OpenRouterClient(**kwargs)
    service = AIService(db, client=client)
    settings = service.get_settings()
    return APIResponse(success=True, data=settings.model_dump())
