# Source: Doc 02 §2.6 — Trend analysis service
"""Trend analiz iş mantığı katmanı — dip ve kırılım adaylarını tespit eder."""

import logging
from datetime import date, datetime
from decimal import Decimal

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.indicators.trend import (
    compute_full_indicators,
    detect_macd_crossover,
    detect_support_resistance,
    detect_trend_status,
    score_breakout_candidate,
    score_dip_candidate,
)
from app.repositories.market_repository import (
    IndexRepository,
    OHLCVRepository,
    SymbolRepository,
)
from app.schemas.analysis import (
    BreakoutCandidateResponse,
    DipCandidateResponse,
    TrendAnalysisMeta,
    TrendAnalysisResponse,
    TrendIndicators,
)

logger = logging.getLogger(__name__)


class TrendAnalysisService:
    """Trend analiz iş mantığı — dip ve kırılım adaylarını tespit eder."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.symbol_repo = SymbolRepository(db)
        self.index_repo = IndexRepository(db)
        self.ohlcv_repo = OHLCVRepository(db)

    async def analyze_trends(
        self,
        period: str = "daily",
        index: str = "ALL",
        trend_type: str = "all",
        min_score: float = 0.6,
        limit: int = 50,
    ) -> tuple[TrendAnalysisResponse, TrendAnalysisMeta]:
        """Ana trend analiz fonksiyonu.

        1. Sembolleri filtrele (endeks bazlı)
        2. Her sembol için OHLCV verisi çek
        3. Göstergeleri hesapla + dip/kırılım skorla
        4. Eşik üstündekileri döndür
        """
        # 1. Sembolleri getir
        symbols = await self._get_symbols_for_index(index)
        if not symbols:
            return self._empty_response(period, index), TrendAnalysisMeta(
                analysis_timestamp=datetime.utcnow()
            )

        dip_candidates: list[DipCandidateResponse] = []
        breakout_candidates: list[BreakoutCandidateResponse] = []

        for symbol in symbols:
            try:
                df = await self._get_ohlcv_dataframe(symbol.ticker)
                if df.empty or len(df) < 50:
                    continue

                # Dip analizi
                if trend_type in ("all", "dip"):
                    dip_score = score_dip_candidate(df)
                    if dip_score >= min_score:
                        candidate = await self._build_dip_candidate(symbol, df, dip_score)
                        dip_candidates.append(candidate)

                # Kırılım analizi
                if trend_type in ("all", "breakout"):
                    breakout_score = score_breakout_candidate(df)
                    if breakout_score >= min_score:
                        candidate = await self._build_breakout_candidate(symbol, df, breakout_score)
                        breakout_candidates.append(candidate)

            except Exception as e:
                logger.warning(f"Trend analiz hatası ({symbol.ticker}): {e}")
                continue

        # Skorlara göre sırala ve limitle
        dip_candidates.sort(key=lambda c: c.dip_score, reverse=True)
        breakout_candidates.sort(key=lambda c: c.breakout_score, reverse=True)
        dip_candidates = dip_candidates[:limit]
        breakout_candidates = breakout_candidates[:limit]

        response = TrendAnalysisResponse(
            period=period,
            index=index,
            analysis_date=date.today().isoformat(),
            dip_candidates=dip_candidates,
            breakout_candidates=breakout_candidates,
        )

        meta = TrendAnalysisMeta(
            total_dip_candidates=len(dip_candidates),
            total_breakout_candidates=len(breakout_candidates),
            analysis_timestamp=datetime.utcnow(),
        )

        return response, meta

    # ── Yardımcı Metotlar ──

    async def _get_symbols_for_index(self, index: str):
        """Endeks koduna göre sembolleri getir."""
        if index == "ALL":
            return await self.symbol_repo.get_active_symbols(skip=0, limit=200)
        return await self.index_repo.get_index_symbols(index)

    async def _get_ohlcv_dataframe(self, ticker: str) -> pd.DataFrame:
        """Sembol için OHLCV verisini pandas DataFrame olarak döndür."""
        rows = await self.ohlcv_repo.get_by_ticker(ticker, limit=250)
        if not rows:
            return pd.DataFrame()

        data = []
        for row in rows:
            data.append({
                "time": row.time,
                "open": float(row.open),
                "high": float(row.high),
                "low": float(row.low),
                "close": float(row.close),
                "volume": float(row.volume),
            })

        df = pd.DataFrame(data)
        if not df.empty:
            df = df.sort_values("time").reset_index(drop=True)
        return df

    async def _build_dip_candidate(self, symbol, df: pd.DataFrame, dip_score: float) -> DipCandidateResponse:
        """Dip adayı response oluştur."""
        indicators = compute_full_indicators(df)
        close = df["close"]
        price = float(close.iloc[-1])

        # Değişim yüzdesi
        if len(close) >= 2:
            prev_price = float(close.iloc[-2])
            change_pct = ((price - prev_price) / prev_price * 100) if prev_price > 0 else 0.0
        else:
            change_pct = 0.0

        return DipCandidateResponse(
            symbol=symbol.ticker,
            name=symbol.name,
            price=Decimal(str(round(price, 2))),
            change_pct=round(change_pct, 2),
            dip_score=dip_score,
            support_level=indicators.get("support_level"),
            resistance_level=indicators.get("resistance_level"),
            rsi=indicators.get("rsi"),
            macd_signal=indicators.get("macd_crossover", "neutral"),
            volume_ratio=indicators.get("volume_ratio"),
            trend_status=detect_trend_status(close, df["high"], df["low"]),
            indicators=TrendIndicators(
                sma_20=indicators.get("sma_20"),
                sma_50=indicators.get("sma_50"),
                ema_12=indicators.get("ema_12"),
                bollinger_lower=indicators.get("bb_lower"),
                bollinger_upper=indicators.get("bb_upper"),
                adx=indicators.get("adx"),
                stochastic_k=indicators.get("stoch_k"),
                macd_histogram=indicators.get("macd_histogram"),
                obv_trend=indicators.get("obv_trend"),
            ),
        )

    async def _build_breakout_candidate(self, symbol, df: pd.DataFrame, breakout_score: float) -> BreakoutCandidateResponse:
        """Kırılım adayı response oluştur."""
        indicators = compute_full_indicators(df)
        close = df["close"]
        price = float(close.iloc[-1])

        # Değişim yüzdesi
        if len(close) >= 2:
            prev_price = float(close.iloc[-2])
            change_pct = ((price - prev_price) / prev_price * 100) if prev_price > 0 else 0.0
        else:
            change_pct = 0.0

        # Hedef fiyat: direnç seviyesi + %5
        resistance = indicators.get("resistance_level")
        target_price = round(resistance * 1.05, 2) if resistance else None

        return BreakoutCandidateResponse(
            symbol=symbol.ticker,
            name=symbol.name,
            price=Decimal(str(round(price, 2))),
            change_pct=round(change_pct, 2),
            breakout_score=breakout_score,
            breakout_level=resistance,
            target_price=target_price,
            volume_surge=indicators.get("volume_ratio"),
            trend_status=detect_trend_status(close, df["high"], df["low"]),
            indicators=TrendIndicators(
                sma_20=indicators.get("sma_20"),
                sma_50=indicators.get("sma_50"),
                ema_12=indicators.get("ema_12"),
                bollinger_lower=indicators.get("bb_lower"),
                bollinger_upper=indicators.get("bb_upper"),
                adx=indicators.get("adx"),
                stochastic_k=indicators.get("stoch_k"),
                macd_histogram=indicators.get("macd_histogram"),
                obv_trend=indicators.get("obv_trend"),
            ),
        )

    def _empty_response(self, period: str, index: str) -> TrendAnalysisResponse:
        return TrendAnalysisResponse(
            period=period,
            index=index,
            analysis_date=date.today().isoformat(),
        )
