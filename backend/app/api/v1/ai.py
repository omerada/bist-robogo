# Source: Doc 10 §Faz 3 Sprint 3.1 + 3.3 — AI API endpoint'leri
"""AI analiz, sohbet, sinyal, deney ve performans endpoint'leri."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.ai import (
    AIAnalysisRequest,
    AIChatRequest,
    AIExperimentCreate,
    AIPerformanceRequest,
    AISettingsRequest,
)
from app.schemas.common import APIResponse
from app.services.ai_experiment_service import AIExperimentService
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
        user_id=user.id,
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
@router.get("/signals/", include_in_schema=False)
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
@router.get("/models/", include_in_schema=False)
async def list_models(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Kullanılabilir OpenRouter modellerini listele."""
    service = AIService(db)
    models = await service.list_models()
    return APIResponse(success=True, data=models.model_dump())


@router.get("/settings")
@router.get("/settings/", include_in_schema=False)
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


# ── A/B Test Deney Endpoint'leri ──


@router.post("/experiments")
async def create_experiment(
    request: AIExperimentCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Yeni A/B test deneyi oluştur."""
    service = AIExperimentService(db)
    experiment = await service.create_experiment(user.id, request)
    return APIResponse(success=True, data=experiment.model_dump())


@router.get("/experiments")
@router.get("/experiments/", include_in_schema=False)
async def list_experiments(
    status: str | None = Query(default=None, description="Filtre: pending/running/completed/failed"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Kullanıcının A/B test deneylerini listele."""
    service = AIExperimentService(db)
    experiments, total = await service.list_experiments(
        user.id, status=status, skip=skip, limit=limit
    )
    return APIResponse(
        success=True,
        data={
            "experiments": [e.model_dump() for e in experiments],
            "total": total,
        },
    )


@router.get("/experiments/{experiment_id}")
async def get_experiment(
    experiment_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deney detayını sonuçlarıyla birlikte getir."""
    service = AIExperimentService(db)
    experiment = await service.get_experiment(experiment_id, user.id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Deney bulunamadı")
    return APIResponse(success=True, data=experiment.model_dump())


@router.post("/experiments/{experiment_id}/run")
async def run_experiment(
    experiment_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """A/B test deneyini çalıştır."""
    service = AIExperimentService(db)
    experiment = await service.run_experiment(experiment_id, user.id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Deney bulunamadı")
    return APIResponse(success=True, data=experiment.model_dump())


@router.delete("/experiments/{experiment_id}", status_code=204)
async def delete_experiment(
    experiment_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deneyi sil."""
    service = AIExperimentService(db)
    deleted = await service.delete_experiment(experiment_id, user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Deney bulunamadı")


# ── Performans Endpoint'leri ──


@router.get("/performance")
@router.get("/performance/", include_in_schema=False)
async def get_performance(
    model_id: str | None = Query(default=None),
    symbol: str | None = Query(default=None),
    days: int = Query(default=30, ge=1, le=365),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """AI model performans özetini getir."""
    service = AIExperimentService(db)
    summary = await service.get_model_performance(
        model_id=model_id, symbol=symbol, days=days
    )
    return APIResponse(success=True, data=summary.model_dump())


@router.get("/performance/compare")
async def compare_models(
    model_a: str = Query(..., description="A modeli ID"),
    model_b: str = Query(..., description="B modeli ID"),
    days: int = Query(default=30, ge=1, le=365),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """İki AI modelini karşılaştır."""
    service = AIExperimentService(db)
    comparison = await service.get_model_comparison(
        model_a_id=model_a, model_b_id=model_b, days=days
    )
    return APIResponse(success=True, data=comparison.model_dump())
