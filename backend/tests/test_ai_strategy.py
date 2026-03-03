"""AI Strategy testleri — Sprint 3.2.

AIStrategy sınıfı, strateji registry entegrasyonu, Celery task ve fallback testleri.
"""

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pandas as pd

pytestmark = pytest.mark.asyncio(loop_scope="session")


# ── Test DataFrame Oluşturucu ──

def _make_ohlcv(n: int = 100, base_price: float = 50.0) -> pd.DataFrame:
    """Test için OHLCV DataFrame oluştur."""
    np.random.seed(42)
    closes = [base_price]
    for _ in range(n - 1):
        change = np.random.normal(0, 0.02)
        closes.append(closes[-1] * (1 + change))

    closes = np.array(closes)
    highs = closes * (1 + np.random.uniform(0.001, 0.02, n))
    lows = closes * (1 - np.random.uniform(0.001, 0.02, n))
    opens = closes * (1 + np.random.uniform(-0.01, 0.01, n))
    volumes = np.random.randint(100000, 1000000, n)

    return pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    })


# ═══════════════════════════════════════════════════════════════
# 1. AIStrategy Temel Testler
# ═══════════════════════════════════════════════════════════════

class TestAIStrategyBasics:
    """AIStrategy sınıfı temel özellik testleri."""

    def test_strategy_name(self):
        """AIStrategy.name property."""
        from app.strategies.ai_strategy import AIStrategy

        strategy = AIStrategy()
        assert strategy.name == "ai_trend"

    def test_strategy_description(self):
        """AIStrategy.description property."""
        from app.strategies.ai_strategy import AIStrategy

        strategy = AIStrategy()
        assert "OpenRouter" in strategy.description
        assert "LLM" in strategy.description

    def test_validate_params_defaults(self):
        """Varsayılan parametreler."""
        from app.strategies.ai_strategy import AIStrategy

        strategy = AIStrategy()
        params = strategy.validate_params(None)
        assert params["model"] is None
        assert params["temperature"] == 0.3
        assert params["include_indicators"] is True

    def test_validate_params_override(self):
        """Parametre override."""
        from app.strategies.ai_strategy import AIStrategy

        strategy = AIStrategy()
        params = strategy.validate_params({
            "model": "openai/gpt-4o",
            "temperature": 0.7,
        })
        assert params["model"] == "openai/gpt-4o"
        assert params["temperature"] == 0.7

    def test_validate_params_invalid_temperature(self):
        """Geçersiz temperature değeri."""
        from app.strategies.ai_strategy import AIStrategy

        strategy = AIStrategy()
        with pytest.raises(ValueError, match="temperature"):
            strategy.validate_params({"temperature": 3.0})

    def test_validate_params_negative_temperature(self):
        """Negatif temperature değeri."""
        from app.strategies.ai_strategy import AIStrategy

        strategy = AIStrategy()
        with pytest.raises(ValueError, match="temperature"):
            strategy.validate_params({"temperature": -0.5})

    def test_is_base_strategy_subclass(self):
        """AIStrategy BaseStrategy'den türetilmiş."""
        from app.strategies.ai_strategy import AIStrategy
        from app.strategies.base import BaseStrategy

        assert issubclass(AIStrategy, BaseStrategy)

    def test_confidence_map_values(self):
        """Confidence mapping doğru değerler."""
        from app.strategies.ai_strategy import _CONFIDENCE_MAP

        assert _CONFIDENCE_MAP["high"] == 0.85
        assert _CONFIDENCE_MAP["medium"] == 0.60
        assert _CONFIDENCE_MAP["low"] == 0.35


# ═══════════════════════════════════════════════════════════════
# 2. AIStrategy Analyze Testleri (Mocked LLM)
# ═══════════════════════════════════════════════════════════════

class TestAIStrategyAnalyze:
    """AIStrategy.analyze() — LLM mock'lanmış testler."""

    async def test_analyze_buy_signal(self):
        """LLM BUY sinyali döndüğünde StrategySignal BUY olmalı."""
        from app.strategies.ai_strategy import AIStrategy
        from app.strategies.base import SignalType

        mock_response = {
            "action": "buy",
            "confidence": "high",
            "summary": "Güçlü alım sinyali",
            "reasoning": "RSI düşük, MACD kesişimi pozitif",
            "key_factors": ["RSI < 30", "Golden Cross"],
            "target_price": 55.0,
            "stop_loss": 48.0,
            "risk_level": "medium",
        }

        with patch("app.core.openrouter_client.OpenRouterClient") as MockClient:
            instance = MockClient.return_value
            instance.get_json = AsyncMock(return_value=mock_response)
            instance.model = "google/gemini-2.5-flash"
            instance.temperature = 0.3

            strategy = AIStrategy()
            ohlcv = _make_ohlcv(100)
            signal = await strategy.analyze("THYAO", ohlcv)

            assert signal.signal_type == SignalType.BUY
            assert signal.confidence == 0.85
            assert signal.symbol == "THYAO"
            assert signal.target_price == Decimal("55.0")
            assert signal.stop_loss == Decimal("48.0")
            assert "Güçlü alım sinyali" in signal.reason
            assert signal.metadata["source"] == "openrouter_llm"

    async def test_analyze_sell_signal(self):
        """LLM SELL sinyali."""
        from app.strategies.ai_strategy import AIStrategy
        from app.strategies.base import SignalType

        mock_response = {
            "action": "sell",
            "confidence": "medium",
            "summary": "Satım önerisi",
            "reasoning": "RSI aşırı alım",
            "key_factors": ["RSI > 70"],
            "target_price": None,
            "stop_loss": None,
            "risk_level": "high",
        }

        with patch("app.core.openrouter_client.OpenRouterClient") as MockClient:
            instance = MockClient.return_value
            instance.get_json = AsyncMock(return_value=mock_response)
            instance.model = "google/gemini-2.5-flash"
            instance.temperature = 0.3

            strategy = AIStrategy()
            signal = await strategy.analyze("GARAN", _make_ohlcv(100))

            assert signal.signal_type == SignalType.SELL
            assert signal.confidence == 0.60
            assert signal.target_price is None

    async def test_analyze_hold_signal(self):
        """LLM HOLD sinyali."""
        from app.strategies.ai_strategy import AIStrategy
        from app.strategies.base import SignalType

        mock_response = {
            "action": "hold",
            "confidence": "low",
            "summary": "Bekle",
            "reasoning": "Net sinyal yok",
            "key_factors": [],
            "risk_level": "low",
        }

        with patch("app.core.openrouter_client.OpenRouterClient") as MockClient:
            instance = MockClient.return_value
            instance.get_json = AsyncMock(return_value=mock_response)
            instance.model = "google/gemini-2.5-flash"
            instance.temperature = 0.3

            strategy = AIStrategy()
            signal = await strategy.analyze("AKBNK", _make_ohlcv(100))

            assert signal.signal_type == SignalType.HOLD
            assert signal.confidence == 0.35

    async def test_analyze_insufficient_data(self):
        """Yetersiz veri (< 10 bar) → HOLD."""
        from app.strategies.ai_strategy import AIStrategy
        from app.strategies.base import SignalType

        strategy = AIStrategy()
        signal = await strategy.analyze("SISE", _make_ohlcv(5))

        assert signal.signal_type == SignalType.HOLD
        assert signal.confidence == 0.0
        assert "yetersiz" in signal.reason.lower()

    async def test_analyze_empty_dataframe(self):
        """Boş DataFrame → HOLD."""
        from app.strategies.ai_strategy import AIStrategy
        from app.strategies.base import SignalType

        strategy = AIStrategy()
        signal = await strategy.analyze("EREGL", pd.DataFrame())

        assert signal.signal_type == SignalType.HOLD
        assert signal.confidence == 0.0

    async def test_analyze_none_dataframe(self):
        """None DataFrame → HOLD."""
        from app.strategies.ai_strategy import AIStrategy
        from app.strategies.base import SignalType

        strategy = AIStrategy()
        signal = await strategy.analyze("KCHOL", None)

        assert signal.signal_type == SignalType.HOLD
        assert signal.confidence == 0.0


# ═══════════════════════════════════════════════════════════════
# 3. Fallback ve Hata Testleri
# ═══════════════════════════════════════════════════════════════

class TestAIStrategyFallback:
    """AI servisi başarısız olduğunda fallback davranışı."""

    async def test_llm_error_triggers_fallback(self):
        """LLM hatası → fallback signal (HOLD veya basit gösterge sinyali)."""
        from app.strategies.ai_strategy import AIStrategy
        from app.strategies.base import SignalType

        with patch("app.core.openrouter_client.OpenRouterClient") as MockClient:
            instance = MockClient.return_value
            instance.get_json = AsyncMock(side_effect=Exception("API timeout"))
            instance.model = "google/gemini-2.5-flash"
            instance.temperature = 0.3

            strategy = AIStrategy()
            signal = await strategy.analyze("THYAO", _make_ohlcv(100))

            # Fallback çalışmalı — HOLD, BUY veya SELL (gösterge bazlı)
            assert signal.signal_type in [SignalType.BUY, SignalType.SELL, SignalType.HOLD]
            assert signal.metadata.get("source") == "fallback"

    async def test_fallback_signal_direct(self):
        """_fallback_signal direkt çağrılabilir."""
        from app.strategies.ai_strategy import AIStrategy

        strategy = AIStrategy()
        ohlcv = _make_ohlcv(100)
        signal = strategy._fallback_signal("THYAO", ohlcv)

        assert signal.symbol == "THYAO"
        assert signal.metadata is not None
        assert signal.metadata.get("source") == "fallback"

    async def test_model_override(self):
        """params.model override çalışıyor."""
        from app.strategies.ai_strategy import AIStrategy

        mock_response = {
            "action": "hold",
            "confidence": "low",
            "summary": "Test",
            "reasoning": "Test",
            "key_factors": [],
            "risk_level": "low",
        }

        with patch("app.core.openrouter_client.OpenRouterClient") as MockClient:
            instance = MockClient.return_value
            instance.get_json = AsyncMock(return_value=mock_response)
            instance.model = "openai/gpt-4o"
            instance.temperature = 0.3

            strategy = AIStrategy()
            signal = await strategy.analyze(
                "THYAO",
                _make_ohlcv(100),
                params={"model": "openai/gpt-4o"},
            )

            # Model override atanmış olmalı
            assert instance.model == "openai/gpt-4o"


# ═══════════════════════════════════════════════════════════════
# 4. Strategy Registry Testleri
# ═══════════════════════════════════════════════════════════════

class TestStrategyRegistry:
    """STRATEGY_REGISTRY'de ai_trend kayıtlı."""

    def test_ai_trend_in_registry(self):
        """ai_trend STRATEGY_REGISTRY'de bulunuyor."""
        from app.strategies import STRATEGY_REGISTRY

        assert "ai_trend" in STRATEGY_REGISTRY

    def test_registry_instantiate_ai_strategy(self):
        """STRATEGY_REGISTRY üzerinden AIStrategy instantiate edilebilir."""
        from app.strategies import STRATEGY_REGISTRY
        from app.strategies.base import BaseStrategy

        cls = STRATEGY_REGISTRY["ai_trend"]
        instance = cls()
        assert isinstance(instance, BaseStrategy)
        assert instance.name == "ai_trend"

    def test_registry_has_all_strategies(self):
        """Registry 3 strateji içeriyor (ma_crossover, rsi_reversal, ai_trend)."""
        from app.strategies import STRATEGY_REGISTRY

        assert len(STRATEGY_REGISTRY) == 3
        assert "ma_crossover" in STRATEGY_REGISTRY
        assert "rsi_reversal" in STRATEGY_REGISTRY
        assert "ai_trend" in STRATEGY_REGISTRY


# ═══════════════════════════════════════════════════════════════
# 5. Gösterge Hesaplama Testleri
# ═══════════════════════════════════════════════════════════════

class TestAIStrategyIndicators:
    """AIStrategy._compute_indicators testleri."""

    def test_compute_indicators_returns_dict(self):
        """_compute_indicators dict döndürmeli."""
        from app.strategies.ai_strategy import AIStrategy

        strategy = AIStrategy()
        result = strategy._compute_indicators(_make_ohlcv(100))

        assert isinstance(result, dict)
        assert "rsi" in result
        assert "macd" in result
        assert "sma_20" in result
        assert "adx" in result

    def test_compute_indicators_has_volume_ratio(self):
        """Volume ratio hesaplanıyor."""
        from app.strategies.ai_strategy import AIStrategy

        strategy = AIStrategy()
        result = strategy._compute_indicators(_make_ohlcv(100))

        assert "volume_ratio" in result
        assert result["volume_ratio"] is not None

    def test_compute_indicators_short_data(self):
        """Kısa veri → bazı göstergeler None olabilir."""
        from app.strategies.ai_strategy import AIStrategy

        strategy = AIStrategy()
        result = strategy._compute_indicators(_make_ohlcv(15))

        assert isinstance(result, dict)
        # Kısa veride bazı değerler None olabilir ama hata vermemeli

    def test_compute_price_summary(self):
        """_compute_price_summary fiyat bilgisi döndürmeli."""
        from app.strategies.ai_strategy import AIStrategy

        strategy = AIStrategy()
        result = strategy._compute_price_summary("THYAO", _make_ohlcv(100))

        assert result["symbol"] == "THYAO"
        assert "current_price" in result
        assert "change_pct" in result
        assert "high_52w" in result
        assert "low_52w" in result

    def test_build_prompt_content(self):
        """_build_prompt prompt string döndürmeli."""
        from app.strategies.ai_strategy import AIStrategy

        strategy = AIStrategy()
        indicators = {"rsi": 45.2, "macd": 0.5}
        price = {"symbol": "THYAO", "current_price": 50.0, "change_pct": 1.5,
                 "high_52w": 55.0, "low_52w": 40.0, "volume": 500000}

        prompt = strategy._build_prompt("THYAO", indicators, price)

        assert "THYAO" in prompt
        assert "50.0" in prompt
        assert "rsi" in prompt


# ═══════════════════════════════════════════════════════════════
# 6. Celery Task Testleri
# ═══════════════════════════════════════════════════════════════

class TestAITasks:
    """AI Celery task tanım testleri."""

    def test_ai_tasks_registered(self):
        """AI task'ları Celery'de kayıtlı."""
        from app.tasks.ai_tasks import (
            run_ai_analysis,
            run_ai_signals_batch,
            run_ai_strategy,
            run_ai_strategy_batch,
        )

        assert run_ai_analysis.name == "app.tasks.ai_tasks.run_ai_analysis"
        assert run_ai_signals_batch.name == "app.tasks.ai_tasks.run_ai_signals_batch"
        assert run_ai_strategy.name == "app.tasks.ai_tasks.run_ai_strategy"
        assert run_ai_strategy_batch.name == "app.tasks.ai_tasks.run_ai_strategy_batch"

    def test_celery_beat_has_ai_signals(self):
        """Beat schedule'da AI sinyal görevi var."""
        from app.tasks.celery_app import celery_app

        schedule = celery_app.conf.beat_schedule
        assert "daily-ai-signals" in schedule
        assert schedule["daily-ai-signals"]["task"] == "app.tasks.ai_tasks.run_ai_signals_batch"


# ═══════════════════════════════════════════════════════════════
# 7. API Entegrasyon Testleri (Strateji CRUD ile ai_trend)
# ═══════════════════════════════════════════════════════════════

class TestAIStrategyAPI:
    """AI strateji tipiyle CRUD API testleri."""

    async def test_create_ai_strategy(self, auth_client):
        """ai_trend tipinde strateji oluşturma."""
        resp = await auth_client.post(
            "/api/v1/strategies/",
            json={
                "name": "AI Trend Test",
                "description": "LLM tabanlı test stratejisi",
                "strategy_type": "ai_trend",
                "parameters": {"model": "google/gemini-2.5-flash", "temperature": 0.3},
                "symbols": ["THYAO", "GARAN"],
            },
        )
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["strategy_type"] == "ai_trend"
        assert data["name"] == "AI Trend Test"
        assert data["parameters"]["model"] == "google/gemini-2.5-flash"

    async def test_list_ai_strategies(self, auth_client):
        """ai_trend filtresiyle listeleme."""
        # Önce oluştur
        await auth_client.post(
            "/api/v1/strategies/",
            json={
                "name": "AI Filter Test",
                "strategy_type": "ai_trend",
                "parameters": {},
                "symbols": ["AKBNK"],
            },
        )

        resp = await auth_client.get(
            "/api/v1/strategies/",
            params={"strategy_type": "ai_trend"},
        )
        assert resp.status_code == 200
        strategies = resp.json()["data"]
        assert all(s["strategy_type"] == "ai_trend" for s in strategies)

    async def test_activate_ai_strategy(self, auth_client):
        """ai_trend strateji aktivasyon."""
        resp = await auth_client.post(
            "/api/v1/strategies/",
            json={
                "name": "AI Activate Test",
                "strategy_type": "ai_trend",
                "parameters": {"temperature": 0.5},
                "symbols": ["EREGL"],
            },
        )
        strategy_id = resp.json()["data"]["id"]

        resp2 = await auth_client.post(f"/api/v1/strategies/{strategy_id}/activate")
        assert resp2.status_code == 200
        assert resp2.json()["data"]["is_active"] is True

    async def test_deactivate_ai_strategy(self, auth_client):
        """ai_trend strateji deaktivasyon."""
        resp = await auth_client.post(
            "/api/v1/strategies/",
            json={
                "name": "AI Deactivate Test",
                "strategy_type": "ai_trend",
                "parameters": {},
                "symbols": ["SISE"],
            },
        )
        strategy_id = resp.json()["data"]["id"]

        await auth_client.post(f"/api/v1/strategies/{strategy_id}/activate")
        resp2 = await auth_client.post(f"/api/v1/strategies/{strategy_id}/deactivate")
        assert resp2.status_code == 200
        assert resp2.json()["data"]["is_active"] is False

    async def test_delete_ai_strategy(self, auth_client):
        """ai_trend strateji silme."""
        resp = await auth_client.post(
            "/api/v1/strategies/",
            json={
                "name": "AI Delete Test",
                "strategy_type": "ai_trend",
                "parameters": {},
                "symbols": ["KCHOL"],
            },
        )
        strategy_id = resp.json()["data"]["id"]

        resp2 = await auth_client.delete(f"/api/v1/strategies/{strategy_id}")
        assert resp2.status_code == 204
