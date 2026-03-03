# Source: Doc 10 §Faz 3 Sprint 3.1 + 3.3 — AI iş mantığı katmanı
"""AI servisi — OpenRouter LLM ile teknik analiz, sohbet, sinyal üretimi."""

import json
import logging
import time
from datetime import datetime

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.openrouter_client import OpenRouterClient, OpenRouterError
from app.indicators.trend import compute_full_indicators
from app.repositories.ai_repository import AIAnalysisLogRepository
from app.repositories.market_repository import OHLCVRepository, SymbolRepository
from app.schemas.ai import (
    AIAnalysisResponse,
    AIChatMessage,
    AIChatResponse,
    AIConfidence,
    AIIndicatorSummary,
    AIModelInfo,
    AIModelListResponse,
    AISignalAction,
    AISignalListResponse,
    AISignalResponse,
    AISettingsResponse,
)

logger = logging.getLogger(__name__)

# ── Sistem Prompt'ları ──

ANALYSIS_SYSTEM_PROMPT = """Sen BIST (Borsa İstanbul) için uzman bir teknik analiz asistanısın.
Görevin, verilen teknik göstergeleri ve fiyat bilgilerini analiz edip, Türkçe olarak ALIM/SATIM/TUT önerisinde bulunmak.

Kurallar:
- JSON formatında yanıt ver.
- Tek bir hisse için analiz yap.
- Teknik göstergeleri (RSI, MACD, Bollinger, Stochastic, SMA, ADX vb.) yorumla.
- Destek/direnç seviyelerini değerlendir.
- Hacim trendini incele.
- Risk seviyesi belirle (low/medium/high).
- Tüm metin alanları Türkçe olsun.

JSON şablonu:
{
  "action": "buy" | "sell" | "hold",
  "confidence": "low" | "medium" | "high",
  "summary": "Kısa Türkçe analiz özeti",
  "reasoning": "Detaylı gerekçe",
  "key_factors": ["Faktör 1", "Faktör 2"],
  "target_price": null | number,
  "stop_loss": null | number,
  "risk_level": "low" | "medium" | "high"
}"""

CHAT_SYSTEM_PROMPT = """Sen BIST (Borsa İstanbul) odaklı bir finans ve yatırım asistanısın.
Görevin kullanıcıların piyasa, hisse, teknik analiz ve yatırım stratejileri hakkındaki sorularını yanıtlamak.

Kurallar:
- Türkçe yanıt ver.
- Somut ve anlaşılır bilgi sun.
- Yatırım tavsiyesi verdiğinde, bunun AI tarafından üretildiğini belirt.
- Teknik göstergeleri açıklarken pratik örnekler kullan.
- Spekülasyondan kaçın, elden geldiğince veriye dayalı ol."""

SIGNALS_SYSTEM_PROMPT = """Sen BIST (Borsa İstanbul) için teknik analiz uzmanısın.
Birden fazla hissenin göstergelerini değerlendirip, en güçlü AL/SAT sinyallerini belirle.

Kurallar:
- JSON formatında yanıt ver.
- Her sinyal için sembol, aksiyon, güven seviyesi, sebep ve skor (0-1) belirle.
- Sadece güçlü sinyalleri raporla (skor > 0.5).
- Türkçe sebep yaz.

JSON şablonu:
{
  "signals": [
    {"symbol": "THYAO", "action": "buy"|"sell"|"hold", "confidence": "low"|"medium"|"high", "reason": "...", "score": 0.85}
  ]
}"""


class AIService:
    """AI iş mantığı — OpenRouter LLM ile sembol analizi, sohbet, sinyal üretimi."""

    def __init__(self, db: AsyncSession, client: OpenRouterClient | None = None):
        self.db = db
        self.client = client or OpenRouterClient()
        self.symbol_repo = SymbolRepository(db)
        self.ohlcv_repo = OHLCVRepository(db)
        self.log_repo = AIAnalysisLogRepository(db)

    # ── Sembol Analizi ──

    async def analyze_symbol(
        self,
        symbol: str,
        period: str = "daily",
        include_indicators: bool = True,
        user_id=None,
    ) -> AIAnalysisResponse:
        """Bir sembolün teknik verilerini toplayıp AI'dan analiz ister.

        1. OHLCV verisi çek
        2. Teknik göstergeleri hesapla
        3. LLM'e gönder
        4. Yapılandırılmış yanıt dön
        5. Performans logla
        """
        start = time.monotonic()

        # 1. Gösterge verisi topla
        indicators_data = {}
        if include_indicators:
            indicators_data = await self._get_symbol_indicators(symbol)

        # 2. Fiyat bilgisi
        price_info = await self._get_price_summary(symbol)

        # 3. LLM prompt oluştur
        user_content = self._build_analysis_prompt(symbol, indicators_data, price_info)

        # 4. LLM'den yanıt al
        try:
            result = await self.client.get_json(
                messages=[
                    {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ]
            )
        except OpenRouterError:
            # Fallback: Gösterge bazlı basit analiz
            result = self._fallback_analysis(symbol, indicators_data)

        latency_ms = int((time.monotonic() - start) * 1000)

        # 5. Yanıtı şemaya dönüştür
        indicators_summary = AIIndicatorSummary(**indicators_data) if indicators_data else None

        action = AISignalAction(result.get("action", "hold"))
        confidence = AIConfidence(result.get("confidence", "low"))

        # 6. Performans logla (fire-and-forget, hata durumunda devam et)
        try:
            score = float(result.get("score", 0.5))
            await self.log_repo.log_analysis(
                symbol=symbol,
                model_id=self.client.model,
                action=action.value,
                confidence=confidence.value,
                score=score,
                latency_ms=latency_ms,
                token_usage=result.get("usage", {}),
                user_id=user_id,
                metadata={"period": period, "include_indicators": include_indicators},
            )
            await self.db.commit()
        except Exception as exc:
            logger.warning("Analiz log kaydı başarısız: %s", exc)

        return AIAnalysisResponse(
            symbol=symbol,
            action=action,
            confidence=confidence,
            summary=result.get("summary", "Analiz yapılamadı"),
            reasoning=result.get("reasoning", ""),
            key_factors=result.get("key_factors", []),
            target_price=result.get("target_price"),
            stop_loss=result.get("stop_loss"),
            risk_level=result.get("risk_level", "medium"),
            indicators=indicators_summary,
            model_used=self.client.model,
            analyzed_at=datetime.utcnow(),
        )

    # ── Sohbet ──

    async def chat(
        self,
        messages: list[AIChatMessage],
        symbol: str | None = None,
    ) -> AIChatResponse:
        """AI sohbet — kullanıcı mesajlarına bağlam dahil yanıt üret."""
        chat_messages: list[dict[str, str]] = [
            {"role": "system", "content": CHAT_SYSTEM_PROMPT}
        ]

        # Sembol bağlamı varsa ekle
        if symbol:
            indicators = await self._get_symbol_indicators(symbol)
            if indicators:
                context = f"Kullanıcı {symbol} hissesi hakkında soru soruyor. Güncel göstergeler: {json.dumps(indicators, ensure_ascii=False)}"
                chat_messages.append({"role": "system", "content": context})

        # Kullanıcı mesajlarını ekle
        for msg in messages:
            chat_messages.append({"role": msg.role.value, "content": msg.content})

        try:
            data = await self.client.chat_completion(chat_messages)
            choices = data.get("choices", [])
            reply = choices[0]["message"]["content"] if choices else "Yanıt üretilemedi."
            usage = data.get("usage", {})
        except OpenRouterError as exc:
            reply = f"AI yanıtı alınamadı: {exc.message}"
            usage = {}

        return AIChatResponse(
            reply=reply,
            model_used=self.client.model,
            usage=usage,
        )

    # ── Sinyal Üretimi ──

    async def generate_signals(
        self,
        symbols: list[str] | None = None,
        limit: int = 10,
    ) -> AISignalListResponse:
        """Birden fazla sembol için AI tabanlı sinyal üret.

        symbols None ise aktif sembollerden seçer.
        """
        if not symbols:
            # Aktif BIST-30 sembollerini al
            all_symbols = await self.symbol_repo.get_active_symbols(limit=30)
            symbols = [s.ticker for s in all_symbols[:30]]

        if not symbols:
            return AISignalListResponse(signals=[], model_used=self.client.model)

        # Her sembol için gösterge topla
        all_indicators = {}
        for sym in symbols[:limit]:
            indicators = await self._get_symbol_indicators(sym)
            if indicators:
                all_indicators[sym] = indicators

        if not all_indicators:
            return AISignalListResponse(signals=[], model_used=self.client.model)

        # LLM'e gönder
        user_content = "Aşağıdaki hisselerin teknik göstergelerini değerlendir ve sinyal üret:\n\n"
        for sym, ind in all_indicators.items():
            user_content += f"**{sym}:** {json.dumps(ind, ensure_ascii=False)}\n\n"

        try:
            result = await self.client.get_json(
                messages=[
                    {"role": "system", "content": SIGNALS_SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ]
            )
        except OpenRouterError:
            return AISignalListResponse(signals=[], model_used=self.client.model)

        # Parse
        raw_signals = result.get("signals", [])
        signals = []
        for sig in raw_signals:
            try:
                signals.append(
                    AISignalResponse(
                        symbol=sig["symbol"],
                        action=AISignalAction(sig.get("action", "hold")),
                        confidence=AIConfidence(sig.get("confidence", "low")),
                        reason=sig.get("reason", ""),
                        score=float(sig.get("score", 0.5)),
                    )
                )
            except (KeyError, ValueError) as exc:
                logger.warning("Sinyal parse hatası: %s — %s", sig, exc)

        return AISignalListResponse(
            signals=signals,
            model_used=self.client.model,
            generated_at=datetime.utcnow(),
        )

    # ── Model Listesi ──

    async def list_models(self) -> AIModelListResponse:
        """Kullanılabilir OpenRouter modellerini listele."""
        try:
            raw_models = await self.client.list_models()
        except OpenRouterError:
            raw_models = []

        models = []
        for m in raw_models[:50]:  # En fazla 50 model göster
            models.append(
                AIModelInfo(
                    id=m.get("id", ""),
                    name=m.get("name", m.get("id", "")),
                    context_length=m.get("context_length"),
                    pricing={
                        "prompt": m.get("pricing", {}).get("prompt", ""),
                        "completion": m.get("pricing", {}).get("completion", ""),
                    },
                )
            )

        return AIModelListResponse(models=models)

    # ── AI Ayarları ──

    def get_settings(self) -> AISettingsResponse:
        """Mevcut AI ayarlarını döner."""
        return AISettingsResponse(
            model=self.client.model,
            temperature=self.client.temperature,
            max_tokens=self.client.max_tokens,
            base_url=self.client.base_url,
            api_key_set=bool(self.client.api_key),
        )

    # ── Yardımcı Fonksiyonlar ──

    async def _get_symbol_indicators(self, symbol: str) -> dict:
        """Sembol için teknik göstergeleri hesapla."""
        try:
            ohlcv_data = await self.ohlcv_repo.get_ohlcv(symbol, interval="1d", limit=100)
            if not ohlcv_data or len(ohlcv_data) < 26:
                return {}

            df = pd.DataFrame(ohlcv_data)
            # get_ohlcv zaten dict listesi döner: time, open, high, low, close, volume
            return compute_full_indicators(df)
        except Exception as exc:
            logger.warning("Gösterge hesaplama hatası (%s): %s", symbol, exc)
            return {}

    async def _get_price_summary(self, symbol: str) -> dict:
        """Sembol için güncel fiyat özeti."""
        try:
            latest = await self.ohlcv_repo.get_latest_price(symbol)
            if not latest:
                return {}
            return latest
        except Exception as exc:
            logger.warning("Fiyat özeti hatası (%s): %s", symbol, exc)
            return {}

    def _build_analysis_prompt(self, symbol: str, indicators: dict, price_info: dict) -> str:
        """Analiz prompt'u oluştur."""
        parts = [f"## {symbol} Hisse Analizi\n"]

        if price_info:
            parts.append(f"**Güncel Fiyat Bilgisi:**\n{json.dumps(price_info, ensure_ascii=False, indent=2)}\n")

        if indicators:
            parts.append(f"**Teknik Göstergeler:**\n{json.dumps(indicators, ensure_ascii=False, indent=2)}\n")
        else:
            parts.append("Teknik gösterge verisi mevcut değil. Genel bir değerlendirme yap.\n")

        parts.append(
            "\nBu verilere dayanarak kapsamlı bir analiz yap ve JSON formatında yanıt ver."
        )

        return "\n".join(parts)

    def _fallback_analysis(self, symbol: str, indicators: dict) -> dict:
        """LLM çağrısı başarısız olduğunda gösterge bazlı basit analiz."""
        action = "hold"
        confidence = "low"
        summary = f"{symbol} için AI analizi şu an kullanılamıyor. Gösterge bazlı basit değerlendirme:"
        factors = []

        rsi = indicators.get("rsi")
        if rsi is not None:
            if rsi < 30:
                action = "buy"
                factors.append(f"RSI aşırı satım bölgesinde ({rsi})")
            elif rsi > 70:
                action = "sell"
                factors.append(f"RSI aşırı alım bölgesinde ({rsi})")
            else:
                factors.append(f"RSI nötr bölgede ({rsi})")

        macd_cross = indicators.get("macd_crossover")
        if macd_cross == "bullish_crossover":
            if action != "sell":
                action = "buy"
            factors.append("MACD yukarı kesişim")
        elif macd_cross == "bearish_crossover":
            if action != "buy":
                action = "sell"
            factors.append("MACD aşağı kesişim")

        adx = indicators.get("adx")
        if adx is not None:
            if adx > 25:
                confidence = "medium"
                factors.append(f"ADX güçlü trend gösteriyor ({adx})")
            else:
                factors.append(f"ADX zayıf trend ({adx})")

        return {
            "action": action,
            "confidence": confidence,
            "summary": summary,
            "reasoning": " | ".join(factors) if factors else "Yeterli veri yok",
            "key_factors": factors,
            "target_price": None,
            "stop_loss": None,
            "risk_level": "medium",
        }
