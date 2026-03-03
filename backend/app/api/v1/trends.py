# Source: Doc 02 §2.6 + Doc 03 §3.6 — Trend analysis endpoints
"""Trend analizi endpoint'leri."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.analysis import TrendPeriod, TrendType
from app.schemas.common import APIResponse
from app.services.trend_analysis_service import TrendAnalysisService

router = APIRouter()


def get_trend_service(db: AsyncSession = Depends(get_db)) -> TrendAnalysisService:
    return TrendAnalysisService(db)


@router.get("/trends", response_model=APIResponse)
async def get_trend_candidates(
    period: TrendPeriod = Query(TrendPeriod.DAILY, description="Analiz periyodu"),
    index: str = Query("ALL", description="Endeks filtresi: XU030, XU100, XKTUM, ALL"),
    type: TrendType = Query(TrendType.ALL, description="Trend tipi: all, dip, breakout"),
    min_score: float = Query(0.6, ge=0, le=1, description="Minimum skor eşiği"),
    limit: int = Query(50, ge=1, le=200, description="Maksimum sonuç sayısı"),
    service: TrendAnalysisService = Depends(get_trend_service),
):
    """Trend adayı hisseleri döner — dip ve kırılım adayları.

    Tüm aktif semboller teknik göstergeler ile analiz edilir.
    Dip skoru ve kırılım skoru eşik değerinin üstündeki adaylar döner.
    """
    response, meta = await service.analyze_trends(
        period=period.value,
        index=index,
        trend_type=type.value,
        min_score=min_score,
        limit=limit,
    )
    return APIResponse(
        success=True,
        data=response.model_dump(),
        meta=meta.model_dump(),
    )


@router.get("/sectors", response_model=APIResponse)
async def get_sector_analysis(
    service: TrendAnalysisService = Depends(get_trend_service),
):
    """Sektörel trend özeti.

    Her sektördeki ortalama RSI, hacim oranı ve trend durumu.
    Not: Faz 2.2+'de detaylandırılacak.
    """
    # Placeholder — sektörel analiz Faz 2.2'de genişletilecek
    return APIResponse(success=True, data=[])
