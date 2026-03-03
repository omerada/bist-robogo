# Source: Doc 10 §Faz 3 Sprint 3.2 — AI tabanlı strateji
"""AI (LLM) tabanlı strateji — OpenRouter LLM ile teknik analiz sinyali üretir.

Mevcut BaseStrategy arayüzünü implement eder, böylece strateji motoru
tarafından diğer stratejiler (MA Crossover, RSI Reversal) gibi çalıştırılabilir.
"""

import logging
from decimal import Decimal

import pandas as pd

from app.strategies.base import BaseStrategy, SignalType, StrategySignal

logger = logging.getLogger(__name__)

# Confidence mapping: AI string → float score
_CONFIDENCE_MAP = {
    "high": 0.85,
    "medium": 0.60,
    "low": 0.35,
}


class AIStrategy(BaseStrategy):
    """LLM tabanlı strateji — OpenRouter AI servisi üzerinden sinyal üretir.

    analyze() çağrıldığında:
    1. OHLCV verisinden teknik göstergeleri hesaplar
    2. AIService.analyze_symbol() ile LLM'den analiz alır
    3. Sonucu StrategySignal formatına dönüştürür

    Parametreler:
        model: OpenRouter model adı (varsayılan: config'den)
        temperature: LLM sıcaklık (varsayılan: 0.3)
        include_indicators: Göstergeleri dahil et (varsayılan: True)
    """

    DEFAULT_PARAMS = {
        "model": None,  # None → config'deki varsayılan model
        "temperature": 0.3,
        "include_indicators": True,
    }

    @property
    def name(self) -> str:
        return "ai_trend"

    @property
    def description(self) -> str:
        return "AI Trend Analizi — OpenRouter LLM ile teknik gösterge bazlı sinyal üretimi"

    def validate_params(self, params: dict) -> dict:
        """Parametre doğrulama ve varsayılanlarla birleştirme."""
        merged = {**self.DEFAULT_PARAMS, **(params or {})}

        temp = merged.get("temperature", 0.3)
        if not isinstance(temp, (int, float)) or not (0.0 <= temp <= 2.0):
            raise ValueError("temperature 0.0 ile 2.0 arasında olmalı")

        return merged

    async def analyze(
        self,
        symbol: str,
        ohlcv: pd.DataFrame,
        params: dict | None = None,
    ) -> StrategySignal:
        """AI tabanlı analiz — LLM'den yapılandırılmış sinyal üretir.

        Bu metod AIService'i lazy-import eder (circular import önlemi).
        DB session gerektirmez: lightweight httpx client kullanır.
        """
        p = self.validate_params(params)

        if ohlcv is None or ohlcv.empty or len(ohlcv) < 10:
            return StrategySignal(
                symbol=symbol,
                signal_type=SignalType.HOLD,
                confidence=0.0,
                reason="AI analizi için yetersiz veri (minimum 10 bar)",
            )

        try:
            # Lazy import: circular dependency önlemi
            from app.core.openrouter_client import OpenRouterClient
            from app.schemas.ai import AISignalAction

            # Client oluştur (opsiyonel model override ile)
            client = OpenRouterClient()
            if p.get("model"):
                client.model = p["model"]
            if p.get("temperature") is not None:
                client.temperature = p["temperature"]

            # Gösterge hesapla → prompt context
            indicator_context = self._compute_indicators(ohlcv)
            price_context = self._compute_price_summary(symbol, ohlcv)

            # LLM'den analiz iste
            from app.services.ai_service import ANALYSIS_SYSTEM_PROMPT

            user_content = self._build_prompt(symbol, indicator_context, price_context)

            result = await client.get_json(
                messages=[
                    {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ]
            )

            # Yanıtı StrategySignal'a dönüştür
            action = result.get("action", "hold").lower()
            confidence_str = result.get("confidence", "low").lower()
            confidence = _CONFIDENCE_MAP.get(confidence_str, 0.35)

            signal_type = {
                "buy": SignalType.BUY,
                "sell": SignalType.SELL,
            }.get(action, SignalType.HOLD)

            target_price = (
                Decimal(str(result["target_price"]))
                if result.get("target_price")
                else None
            )
            stop_loss = (
                Decimal(str(result["stop_loss"]))
                if result.get("stop_loss")
                else None
            )

            reason = result.get("summary", "AI analizi tamamlandı")
            key_factors = result.get("key_factors", [])

            return StrategySignal(
                symbol=symbol,
                signal_type=signal_type,
                confidence=confidence,
                target_price=target_price,
                stop_loss=stop_loss,
                take_profit=target_price,  # AI hedef fiyat = take profit
                reason=reason,
                metadata={
                    "reasoning": result.get("reasoning", ""),
                    "key_factors": key_factors,
                    "risk_level": result.get("risk_level", "medium"),
                    "model": client.model,
                    "source": "openrouter_llm",
                },
            )

        except Exception as exc:
            logger.warning(f"AI strateji hatası ({symbol}): {exc}, fallback kullanılıyor")
            return self._fallback_signal(symbol, ohlcv)

    # ── Yardımcı Metotlar ──

    def _compute_indicators(self, ohlcv: pd.DataFrame) -> dict:
        """Teknik göstergeleri hesapla — LLM prompt context'i için."""
        try:
            from app.indicators.momentum import (
                calculate_bollinger_bands,
                calculate_ema,
                calculate_macd,
                calculate_rsi,
                calculate_sma,
                calculate_stochastic,
            )
            from app.indicators.trend import calculate_adx, calculate_obv

            close = ohlcv["close"]
            high = ohlcv["high"]
            low = ohlcv["low"]
            volume = ohlcv["volume"]

            rsi = calculate_rsi(close)
            macd_line, signal_line, histogram = calculate_macd(close)
            bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(close)
            stoch_k, stoch_d = calculate_stochastic(high, low, close)
            sma20 = calculate_sma(close, 20)
            sma50 = calculate_sma(close, 50)
            ema12 = calculate_ema(close, 12)
            adx = calculate_adx(high, low, close)
            obv = calculate_obv(close, volume)

            def _safe(s: pd.Series) -> float | None:
                v = s.iloc[-1] if len(s) > 0 else None
                return round(float(v), 4) if v is not None and pd.notna(v) else None

            # OBV trend: son 5 barın trendi
            obv_trend = "neutral"
            if len(obv) >= 5:
                obv_diff = float(obv.iloc[-1]) - float(obv.iloc[-5])
                if obv_diff > 0:
                    obv_trend = "yükselen"
                elif obv_diff < 0:
                    obv_trend = "düşen"

            # Volume ratio: son bar / 20 günlük ortalama
            vol_ratio = None
            if len(volume) >= 20:
                avg_vol = float(volume.iloc[-20:].mean())
                if avg_vol > 0:
                    vol_ratio = round(float(volume.iloc[-1]) / avg_vol, 2)

            return {
                "rsi": _safe(rsi),
                "macd": _safe(macd_line),
                "macd_signal": _safe(signal_line),
                "macd_histogram": _safe(histogram),
                "stoch_k": _safe(stoch_k),
                "stoch_d": _safe(stoch_d),
                "bb_upper": _safe(bb_upper),
                "bb_middle": _safe(bb_middle),
                "bb_lower": _safe(bb_lower),
                "sma_20": _safe(sma20),
                "sma_50": _safe(sma50),
                "ema_12": _safe(ema12),
                "adx": _safe(adx),
                "obv_trend": obv_trend,
                "volume_ratio": vol_ratio,
            }
        except Exception as exc:
            logger.warning(f"Gösterge hesaplama hatası: {exc}")
            return {}

    def _compute_price_summary(self, symbol: str, ohlcv: pd.DataFrame) -> dict:
        """Son fiyat bilgilerini derle."""
        try:
            last = ohlcv.iloc[-1]
            prev = ohlcv.iloc[-2] if len(ohlcv) >= 2 else last

            current_price = float(last["close"])
            prev_close = float(prev["close"])
            change_pct = ((current_price - prev_close) / prev_close * 100) if prev_close else 0

            # 52 hafta (yaklaşık 252 iş günü)
            lookback = min(252, len(ohlcv))
            high_52w = float(ohlcv["high"].iloc[-lookback:].max())
            low_52w = float(ohlcv["low"].iloc[-lookback:].min())

            return {
                "symbol": symbol,
                "current_price": round(current_price, 4),
                "prev_close": round(prev_close, 4),
                "change_pct": round(change_pct, 2),
                "high_52w": round(high_52w, 4),
                "low_52w": round(low_52w, 4),
                "volume": int(last["volume"]) if pd.notna(last["volume"]) else 0,
            }
        except Exception as exc:
            logger.warning(f"Fiyat özeti hatası: {exc}")
            return {"symbol": symbol}

    def _build_prompt(self, symbol: str, indicators: dict, price: dict) -> str:
        """LLM için kullanıcı prompt'u oluştur."""
        parts = [f"## {symbol} Teknik Analiz Verisi\n"]

        if price:
            parts.append(f"**Fiyat:** {price.get('current_price', 'N/A')} TL")
            parts.append(f"**Değişim:** %{price.get('change_pct', 0)}")
            parts.append(f"**52H Yüksek/Düşük:** {price.get('high_52w', 'N/A')} / {price.get('low_52w', 'N/A')}")
            parts.append(f"**Hacim:** {price.get('volume', 'N/A')}\n")

        if indicators:
            parts.append("**Teknik Göstergeler:**")
            for key, val in indicators.items():
                if val is not None:
                    parts.append(f"- {key}: {val}")

        parts.append(f"\nYukarıdaki veriler ışığında {symbol} için AL/SAT/TUT önerini JSON formatında ver.")

        return "\n".join(parts)

    def _fallback_signal(self, symbol: str, ohlcv: pd.DataFrame) -> StrategySignal:
        """AI servisi başarısız olduğunda gösterge bazlı basit sinyal üret."""
        try:
            from app.indicators.momentum import calculate_rsi, calculate_sma

            close = ohlcv["close"]
            rsi = calculate_rsi(close)
            rsi_val = float(rsi.iloc[-1]) if pd.notna(rsi.iloc[-1]) else 50.0

            sma20 = calculate_sma(close, 20)
            sma50 = calculate_sma(close, 50)
            sma20_val = float(sma20.iloc[-1]) if pd.notna(sma20.iloc[-1]) else 0
            sma50_val = float(sma50.iloc[-1]) if pd.notna(sma50.iloc[-1]) else 0
            current_price = float(close.iloc[-1])

            # Basit kurallar
            if rsi_val < 30 and current_price > sma50_val:
                return StrategySignal(
                    symbol=symbol,
                    signal_type=SignalType.BUY,
                    confidence=0.4,
                    reason=f"Fallback: RSI aşırı satım ({rsi_val:.1f}), fiyat SMA50 üstünde",
                    metadata={"source": "fallback", "rsi": rsi_val},
                )
            elif rsi_val > 70 and current_price < sma20_val:
                return StrategySignal(
                    symbol=symbol,
                    signal_type=SignalType.SELL,
                    confidence=0.4,
                    reason=f"Fallback: RSI aşırı alım ({rsi_val:.1f}), fiyat SMA20 altında",
                    metadata={"source": "fallback", "rsi": rsi_val},
                )
        except Exception:
            pass

        return StrategySignal(
            symbol=symbol,
            signal_type=SignalType.HOLD,
            confidence=0.0,
            reason="AI analizi başarısız, yeterli veri yok",
            metadata={"source": "fallback"},
        )
