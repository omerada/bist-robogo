# Source: Doc 05 §9.1 — RSI Reversal Strategy
"""RSI Mean Reversion (Ortalamaya Dönüş) stratejisi.

RSI aşırı alım/satım bölgelerinde ters sinyal üretir:
- RSI < oversold → BUY (dipten dönüş beklentisi)
- RSI > overbought → SELL (tepeden dönüş beklentisi)
"""

from decimal import Decimal

import pandas as pd

from app.indicators.momentum import (
    calculate_bollinger_bands,
    calculate_rsi,
    calculate_stochastic,
    calculate_volume_ratio,
)
from app.indicators.trend import calculate_adx, detect_support_resistance
from app.strategies.base import BaseStrategy, SignalType, StrategySignal


class RSIReversalStrategy(BaseStrategy):
    """RSI Mean Reversion stratejisi.

    Parametreler:
        rsi_period: RSI periyodu (varsayılan: 14)
        oversold: Aşırı satım eşiği (varsayılan: 30)
        overbought: Aşırı alım eşiği (varsayılan: 70)
        confirm_stochastic: Stochastic ile doğrula (varsayılan: True)
        confirm_volume: Hacim artışı gereksin mi (varsayılan: True)
    """

    DEFAULT_PARAMS = {
        "rsi_period": 14,
        "oversold": 30,
        "overbought": 70,
        "confirm_stochastic": True,
        "confirm_volume": True,
    }

    @property
    def name(self) -> str:
        return "rsi_reversal"

    @property
    def description(self) -> str:
        return "RSI Ortalamaya Dönüş Stratejisi — Aşırı alım/satım bölgelerinde ters sinyal"

    def validate_params(self, params: dict) -> dict:
        merged = {**self.DEFAULT_PARAMS, **(params or {})}
        if merged["oversold"] >= merged["overbought"]:
            raise ValueError("oversold, overbought'dan küçük olmalı")
        return merged

    async def analyze(
        self,
        symbol: str,
        ohlcv: pd.DataFrame,
        params: dict | None = None,
    ) -> StrategySignal:
        """RSI Reversal analizi.

        1. RSI aşırı alım/satım kontrolü
        2. Stochastic doğrulama (opsiyonel)
        3. Bollinger Band pozisyonu
        4. Hacim artışı kontrolü (opsiyonel)
        """
        p = self.validate_params(params)
        close = ohlcv["close"]
        high = ohlcv["high"]
        low = ohlcv["low"]
        volume = ohlcv["volume"]

        if len(close) < 50:
            return StrategySignal(
                symbol=symbol,
                signal_type=SignalType.HOLD,
                confidence=0.0,
                reason="Yetersiz veri",
            )

        # İndikatörler
        rsi = calculate_rsi(close, p["rsi_period"])
        rsi_val = float(rsi.iloc[-1]) if pd.notna(rsi.iloc[-1]) else 50.0

        stoch_k, stoch_d = calculate_stochastic(high, low, close)
        sk = float(stoch_k.iloc[-1]) if pd.notna(stoch_k.iloc[-1]) else 50.0

        bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(close)
        price = float(close.iloc[-1])
        bbl = float(bb_lower.iloc[-1]) if pd.notna(bb_lower.iloc[-1]) else price * 0.95
        bbu = float(bb_upper.iloc[-1]) if pd.notna(bb_upper.iloc[-1]) else price * 1.05

        vol_ratio = calculate_volume_ratio(volume)
        vr = float(vol_ratio.iloc[-1]) if pd.notna(vol_ratio.iloc[-1]) else 1.0

        adx = calculate_adx(high, low, close)
        adx_val = float(adx.iloc[-1]) if pd.notna(adx.iloc[-1]) else 0.0

        support, resistance = detect_support_resistance(high, low, close)

        current_price = Decimal(str(round(price, 4)))

        metadata = {
            "rsi": round(rsi_val, 2),
            "stoch_k": round(sk, 2),
            "bb_lower": round(bbl, 2),
            "bb_upper": round(bbu, 2),
            "volume_ratio": round(vr, 2),
            "adx": round(adx_val, 2),
            "support": support,
            "resistance": resistance,
        }

        # ── Aşırı Satım → BUY ──
        if rsi_val < p["oversold"]:
            confirmations = 0
            max_confirms = 2

            # Stochastic doğrulama
            if p["confirm_stochastic"] and sk < 20:
                confirmations += 1

            # Hacim artışı
            if p["confirm_volume"] and vr > 1.3:
                confirmations += 1

            # Bollinger alt bant yakınlığı
            if price <= bbl * 1.01:
                confirmations += 1
                max_confirms += 1

            confidence = self._calc_confidence(rsi_val, confirmations, max_confirms, "buy", adx_val)

            # Stop-loss: destek seviyesi veya %3 altı
            sl_price = support if support else price * 0.97
            stop_loss = Decimal(str(round(sl_price * 0.98, 4)))
            # Take-profit: BB orta bant veya %5 yukarı
            tp_price = float(bb_middle.iloc[-1]) if pd.notna(bb_middle.iloc[-1]) else price * 1.05
            take_profit = Decimal(str(round(tp_price, 4)))

            return StrategySignal(
                symbol=symbol,
                signal_type=SignalType.BUY,
                confidence=confidence,
                target_price=take_profit,
                stop_loss=stop_loss,
                take_profit=take_profit,
                reason=f"RSI oversold ({rsi_val:.1f}), doğrulama: {confirmations}/{max_confirms}",
                metadata=metadata,
            )

        # ── Aşırı Alım → SELL ──
        if rsi_val > p["overbought"]:
            confirmations = 0
            max_confirms = 2

            if p["confirm_stochastic"] and sk > 80:
                confirmations += 1

            if p["confirm_volume"] and vr > 1.5:
                confirmations += 1

            if price >= bbu * 0.99:
                confirmations += 1
                max_confirms += 1

            confidence = self._calc_confidence(rsi_val, confirmations, max_confirms, "sell", adx_val)

            return StrategySignal(
                symbol=symbol,
                signal_type=SignalType.SELL,
                confidence=confidence,
                reason=f"RSI overbought ({rsi_val:.1f}), doğrulama: {confirmations}/{max_confirms}",
                metadata=metadata,
            )

        # ── Nötr Bölge → HOLD ──
        return StrategySignal(
            symbol=symbol,
            signal_type=SignalType.HOLD,
            confidence=0.0,
            reason=f"RSI nötr bölgede ({rsi_val:.1f})",
            metadata=metadata,
        )

    def _calc_confidence(
        self, rsi: float, confirmations: int, max_confirms: int, direction: str, adx: float
    ) -> float:
        """Sinyal güven skoru hesapla (0.0-1.0)."""
        score = 0.3  # Base

        # RSI derinliği (%30)
        if direction == "buy":
            if rsi < 15:
                score += 0.30
            elif rsi < 20:
                score += 0.25
            elif rsi < 25:
                score += 0.15
            else:
                score += 0.08
        else:
            if rsi > 85:
                score += 0.30
            elif rsi > 80:
                score += 0.25
            elif rsi > 75:
                score += 0.15
            else:
                score += 0.08

        # Doğrulama sayısı (%20)
        if max_confirms > 0:
            confirmation_ratio = confirmations / max_confirms
            score += 0.20 * confirmation_ratio

        # ADX — trend gücü düşükse mean reversion daha güvenilir (%20)
        if adx < 20:
            score += 0.20
        elif adx < 25:
            score += 0.10

        return round(min(score, 1.0), 4)
