# Source: Doc 05 §9.1 — MA Crossover Strategy
"""MA (Hareketli Ortalama) Crossover stratejisi.

SMA/EMA kesişimlerini tespit eder:
- Golden Cross (kısa MA > uzun MA): BUY sinyali
- Death Cross (kısa MA < uzun MA): SELL sinyali
"""

from decimal import Decimal

import pandas as pd

from app.indicators.momentum import calculate_ema, calculate_rsi, calculate_sma
from app.indicators.trend import calculate_adx
from app.strategies.base import BaseStrategy, SignalType, StrategySignal


class MACrossoverStrategy(BaseStrategy):
    """Hareketli Ortalama Crossover stratejisi.

    Parametreler:
        fast_period: Kısa MA periyodu (varsayılan: 20)
        slow_period: Uzun MA periyodu (varsayılan: 50)
        ma_type: "sma" veya "ema" (varsayılan: "sma")
        adx_threshold: Minimum ADX değeri (varsayılan: 20)
    """

    DEFAULT_PARAMS = {
        "fast_period": 20,
        "slow_period": 50,
        "ma_type": "sma",
        "adx_threshold": 20,
    }

    @property
    def name(self) -> str:
        return "ma_crossover"

    @property
    def description(self) -> str:
        return "Hareketli Ortalama Kesişim Stratejisi — Golden/Death Cross sinyalleri"

    def validate_params(self, params: dict) -> dict:
        merged = {**self.DEFAULT_PARAMS, **(params or {})}
        if merged["fast_period"] >= merged["slow_period"]:
            raise ValueError("fast_period, slow_period'dan küçük olmalı")
        if merged["ma_type"] not in ("sma", "ema"):
            raise ValueError("ma_type 'sma' veya 'ema' olmalı")
        return merged

    async def analyze(
        self,
        symbol: str,
        ohlcv: pd.DataFrame,
        params: dict | None = None,
    ) -> StrategySignal:
        """MA Crossover analizi.

        Golden Cross: kısa MA uzun MA'yı yukarı kesiyor → BUY
        Death Cross: kısa MA uzun MA'yı aşağı kesiyor → SELL
        """
        p = self.validate_params(params)
        close = ohlcv["close"]

        if len(close) < p["slow_period"] + 5:
            return StrategySignal(
                symbol=symbol,
                signal_type=SignalType.HOLD,
                confidence=0.0,
                reason="Yetersiz veri",
            )

        # MA hesapla
        ma_func = calculate_ema if p["ma_type"] == "ema" else calculate_sma
        fast_ma = ma_func(close, p["fast_period"])
        slow_ma = ma_func(close, p["slow_period"])

        # Son 2 bar'ın MA farkları
        prev_diff = float(fast_ma.iloc[-2]) - float(slow_ma.iloc[-2])
        curr_diff = float(fast_ma.iloc[-1]) - float(slow_ma.iloc[-1])

        if pd.isna(prev_diff) or pd.isna(curr_diff):
            return StrategySignal(
                symbol=symbol,
                signal_type=SignalType.HOLD,
                confidence=0.0,
                reason="Gösterge hesaplanamadı",
            )

        # ADX ile trend gücü kontrol
        adx = calculate_adx(ohlcv["high"], ohlcv["low"], close)
        adx_val = float(adx.iloc[-1]) if pd.notna(adx.iloc[-1]) else 0.0
        has_trend = adx_val >= p["adx_threshold"]

        # RSI ile aşırı alım/satım kontrolü
        rsi = calculate_rsi(close)
        rsi_val = float(rsi.iloc[-1]) if pd.notna(rsi.iloc[-1]) else 50.0

        current_price = Decimal(str(round(float(close.iloc[-1]), 4)))

        metadata = {
            "fast_ma": round(float(fast_ma.iloc[-1]), 4),
            "slow_ma": round(float(slow_ma.iloc[-1]), 4),
            "adx": round(adx_val, 2),
            "rsi": round(rsi_val, 2),
            "ma_type": p["ma_type"],
        }

        # Golden Cross — BUY
        if prev_diff <= 0 and curr_diff > 0:
            confidence = self._calc_confidence(adx_val, has_trend, rsi_val, "buy")
            # Stop-loss: son düşük fiyatın %3 altı
            recent_low = float(ohlcv["low"].iloc[-10:].min())
            stop_loss = Decimal(str(round(recent_low * 0.97, 4)))
            # Take-profit: fiyattan %5 yukarı
            take_profit = Decimal(str(round(float(current_price) * 1.05, 4)))

            return StrategySignal(
                symbol=symbol,
                signal_type=SignalType.BUY,
                confidence=confidence,
                target_price=take_profit,
                stop_loss=stop_loss,
                take_profit=take_profit,
                reason=f"Golden Cross: {p['ma_type'].upper()}{p['fast_period']} > {p['ma_type'].upper()}{p['slow_period']}",
                metadata=metadata,
            )

        # Death Cross — SELL
        if prev_diff >= 0 and curr_diff < 0:
            confidence = self._calc_confidence(adx_val, has_trend, rsi_val, "sell")

            return StrategySignal(
                symbol=symbol,
                signal_type=SignalType.SELL,
                confidence=confidence,
                reason=f"Death Cross: {p['ma_type'].upper()}{p['fast_period']} < {p['ma_type'].upper()}{p['slow_period']}",
                metadata=metadata,
            )

        # Crossover yok → HOLD
        return StrategySignal(
            symbol=symbol,
            signal_type=SignalType.HOLD,
            confidence=0.0,
            reason="Crossover yok",
            metadata=metadata,
        )

    def _calc_confidence(self, adx: float, has_trend: bool, rsi: float, direction: str) -> float:
        """Sinyal güven skoru hesapla (0.0-1.0)."""
        score = 0.4  # Base

        # ADX ile trend gücü (%30)
        if has_trend:
            score += 0.15
            if adx > 30:
                score += 0.15
            elif adx > 25:
                score += 0.10

        # RSI doğrulama (%30)
        if direction == "buy" and rsi < 40:
            score += 0.20
        elif direction == "buy" and rsi < 50:
            score += 0.10
        elif direction == "sell" and rsi > 60:
            score += 0.20
        elif direction == "sell" and rsi > 50:
            score += 0.10

        return round(min(score, 1.0), 4)
