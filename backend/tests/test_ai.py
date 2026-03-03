"""AI API testleri — Sprint 3.1."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

pytestmark = pytest.mark.asyncio(loop_scope="session")


class TestAISchemas:
    """AI şema testleri."""

    def test_analysis_request_defaults(self):
        """AIAnalysisRequest varsayılanları."""
        from app.schemas.ai import AIAnalysisRequest

        req = AIAnalysisRequest(symbol="THYAO")
        assert req.symbol == "THYAO"
        assert req.period == "daily"
        assert req.include_indicators is True

    def test_analysis_response_model(self):
        """AIAnalysisResponse model oluşturma."""
        from app.schemas.ai import AIAnalysisResponse

        resp = AIAnalysisResponse(
            symbol="GARAN",
            action="buy",
            confidence="high",
            summary="Test özet",
            reasoning="Test gerekçe",
            key_factors=["RSI düşük"],
            risk_level="medium",
            model_used="test-model",
        )
        assert resp.symbol == "GARAN"
        assert resp.action == "buy"
        assert resp.confidence == "high"
        assert resp.target_price is None

    def test_chat_request_validation(self):
        """AIChatRequest mesaj listesi doğrulama."""
        from app.schemas.ai import AIChatMessage, AIChatRequest

        msg = AIChatMessage(role="user", content="THYAO hakkında ne düşünüyorsun?")
        req = AIChatRequest(messages=[msg])
        assert len(req.messages) == 1
        assert req.symbol is None

    def test_signal_response_score_bounds(self):
        """AISignalResponse skor 0-1 aralığında."""
        from app.schemas.ai import AISignalResponse

        sig = AISignalResponse(
            symbol="THYAO",
            action="buy",
            confidence="high",
            reason="RSI düşük",
            score=0.85,
        )
        assert 0.0 <= sig.score <= 1.0

    def test_signal_response_invalid_score(self):
        """Geçersiz skor → validation error."""
        from pydantic import ValidationError
        from app.schemas.ai import AISignalResponse

        with pytest.raises(ValidationError):
            AISignalResponse(
                symbol="THYAO",
                action="buy",
                confidence="high",
                reason="test",
                score=1.5,
            )

    def test_settings_response(self):
        """AISettingsResponse model."""
        from app.schemas.ai import AISettingsResponse

        settings = AISettingsResponse(
            model="google/gemini-2.5-flash",
            temperature=0.3,
            max_tokens=4096,
            base_url="https://openrouter.ai/api/v1",
            api_key_set=True,
        )
        assert settings.api_key_set is True
        assert settings.temperature == 0.3

    def test_model_info(self):
        """AIModelInfo model."""
        from app.schemas.ai import AIModelInfo

        model = AIModelInfo(id="test/model", name="Test Model", context_length=128000)
        assert model.id == "test/model"
        assert model.context_length == 128000

    def test_settings_request_validation(self):
        """AISettingsRequest temperature 0-2 aralığında."""
        from pydantic import ValidationError
        from app.schemas.ai import AISettingsRequest

        # Geçerli
        req = AISettingsRequest(temperature=1.5, max_tokens=2048)
        assert req.temperature == 1.5

        # Geçersiz temperature
        with pytest.raises(ValidationError):
            AISettingsRequest(temperature=3.0)

    def test_indicator_summary(self):
        """AIIndicatorSummary tüm alanları null olabilir."""
        from app.schemas.ai import AIIndicatorSummary

        summary = AIIndicatorSummary()
        assert summary.rsi is None
        assert summary.macd is None
        assert summary.obv_trend is None

    def test_chat_response(self):
        """AIChatResponse model."""
        from app.schemas.ai import AIChatResponse

        resp = AIChatResponse(reply="Merhaba!", model_used="test")
        assert resp.reply == "Merhaba!"
        assert resp.usage == {}


class TestOpenRouterClient:
    """OpenRouter client birim testleri."""

    def test_client_default_config(self):
        """Client varsayılan ayarları config'den almalı."""
        from app.core.openrouter_client import OpenRouterClient

        client = OpenRouterClient(
            api_key="test-key",
            base_url="https://test.api",
            model="test-model",
        )
        assert client.api_key == "test-key"
        assert client.base_url == "https://test.api"
        assert client.model == "test-model"

    def test_client_headers(self):
        """Client header'ları doğru oluşturmalı."""
        from app.core.openrouter_client import OpenRouterClient

        client = OpenRouterClient(api_key="sk-test-key")
        headers = client._headers()
        assert headers["Authorization"] == "Bearer sk-test-key"
        assert headers["Content-Type"] == "application/json"
        assert "X-Title" in headers

    def test_openrouter_error(self):
        """OpenRouterError exception."""
        from app.core.openrouter_client import OpenRouterError

        err = OpenRouterError(429, "Rate limit exceeded")
        assert err.status_code == 429
        assert "429" in str(err)
        assert "Rate limit" in str(err)


class TestAIService:
    """AI servis birim testleri."""

    def test_fallback_analysis_buy_signal(self):
        """Düşük RSI → buy sinyali."""
        from app.services.ai_service import AIService

        # Mock db
        mock_db = MagicMock()
        service = AIService(mock_db)

        result = service._fallback_analysis("THYAO", {"rsi": 25.0, "adx": 30.0})
        assert result["action"] == "buy"
        assert "RSI" in result["key_factors"][0]
        assert result["confidence"] == "medium"  # ADX > 25

    def test_fallback_analysis_sell_signal(self):
        """Yüksek RSI → sell sinyali."""
        from app.services.ai_service import AIService

        mock_db = MagicMock()
        service = AIService(mock_db)

        result = service._fallback_analysis("GARAN", {"rsi": 75.0})
        assert result["action"] == "sell"

    def test_fallback_analysis_macd_crossover(self):
        """MACD bullish crossover → buy faktörü."""
        from app.services.ai_service import AIService

        mock_db = MagicMock()
        service = AIService(mock_db)

        result = service._fallback_analysis(
            "EREGL", {"rsi": 50.0, "macd_crossover": "bullish_crossover"}
        )
        assert result["action"] == "buy"
        assert any("MACD" in f for f in result["key_factors"])

    def test_fallback_analysis_empty_indicators(self):
        """Gösterge yok → hold + az bilgi."""
        from app.services.ai_service import AIService

        mock_db = MagicMock()
        service = AIService(mock_db)

        result = service._fallback_analysis("AKBNK", {})
        assert result["action"] == "hold"
        assert result["confidence"] == "low"

    def test_build_analysis_prompt(self):
        """Analiz prompt'u oluşturma."""
        from app.services.ai_service import AIService

        mock_db = MagicMock()
        service = AIService(mock_db)

        prompt = service._build_analysis_prompt(
            "THYAO",
            {"rsi": 45.0, "macd": 0.5},
            {"price": 150.0, "volume": 1000000},
        )
        assert "THYAO" in prompt
        assert "rsi" in prompt
        assert "150.0" in prompt

    def test_build_analysis_prompt_no_data(self):
        """Veri yok → uyarı mesajı."""
        from app.services.ai_service import AIService

        mock_db = MagicMock()
        service = AIService(mock_db)

        prompt = service._build_analysis_prompt("AKBNK", {}, {})
        assert "mevcut değil" in prompt

    def test_get_settings(self):
        """Servis ayarları döner."""
        from app.core.openrouter_client import OpenRouterClient
        from app.services.ai_service import AIService

        client = OpenRouterClient(
            api_key="test",
            model="test-model",
            temperature=0.5,
            max_tokens=2048,
        )
        mock_db = MagicMock()
        service = AIService(mock_db, client=client)

        settings = service.get_settings()
        assert settings.model == "test-model"
        assert settings.temperature == 0.5
        assert settings.max_tokens == 2048
        assert settings.api_key_set is True


class TestAIAPI:
    """AI API endpoint testleri."""

    # ── POST /api/v1/ai/analyze ──

    async def test_analyze_unauthenticated(self, client):
        """Auth olmadan → 403."""
        resp = await client.post("/api/v1/ai/analyze", json={"symbol": "THYAO"})
        assert resp.status_code == 403

    async def test_analyze_authenticated(self, auth_client):
        """Analiz endpoint'i çalışmalı (mock OpenRouter)."""
        with patch("app.services.ai_service.AIService.analyze_symbol") as mock:
            from app.schemas.ai import AIAnalysisResponse, AIConfidence, AISignalAction

            mock.return_value = AIAnalysisResponse(
                symbol="THYAO",
                action=AISignalAction.BUY,
                confidence=AIConfidence.HIGH,
                summary="Test analiz",
                reasoning="Test gerekçe",
                key_factors=["RSI düşük"],
                model_used="test-model",
            )

            resp = await auth_client.post(
                "/api/v1/ai/analyze",
                json={"symbol": "THYAO"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["success"] is True
            assert data["data"]["symbol"] == "THYAO"
            assert data["data"]["action"] == "buy"

    # ── POST /api/v1/ai/chat ──

    async def test_chat_unauthenticated(self, client):
        """Auth olmadan → 403."""
        resp = await client.post(
            "/api/v1/ai/chat",
            json={"messages": [{"role": "user", "content": "Merhaba"}]},
        )
        assert resp.status_code == 403

    async def test_chat_authenticated(self, auth_client):
        """Chat endpoint'i çalışmalı (mock)."""
        with patch("app.services.ai_service.AIService.chat") as mock:
            from app.schemas.ai import AIChatResponse

            mock.return_value = AIChatResponse(
                reply="Merhaba! Size nasıl yardımcı olabilirim?",
                model_used="test-model",
            )

            resp = await auth_client.post(
                "/api/v1/ai/chat",
                json={"messages": [{"role": "user", "content": "Merhaba"}]},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["success"] is True
            assert "Merhaba" in data["data"]["reply"]

    async def test_chat_empty_messages(self, auth_client):
        """Boş mesaj listesi → 422."""
        resp = await auth_client.post(
            "/api/v1/ai/chat",
            json={"messages": []},
        )
        assert resp.status_code == 422

    # ── GET /api/v1/ai/signals ──

    async def test_signals_unauthenticated(self, client):
        """Auth olmadan → 403."""
        resp = await client.get("/api/v1/ai/signals")
        assert resp.status_code == 403

    async def test_signals_authenticated(self, auth_client):
        """Sinyal endpoint'i çalışmalı (mock)."""
        with patch("app.services.ai_service.AIService.generate_signals") as mock:
            from app.schemas.ai import AISignalListResponse

            mock.return_value = AISignalListResponse(
                signals=[], model_used="test-model"
            )

            resp = await auth_client.get("/api/v1/ai/signals")
            assert resp.status_code == 200
            data = resp.json()
            assert data["success"] is True
            assert isinstance(data["data"]["signals"], list)

    # ── GET /api/v1/ai/models ──

    async def test_models_unauthenticated(self, client):
        """Auth olmadan → 403."""
        resp = await client.get("/api/v1/ai/models")
        assert resp.status_code == 403

    async def test_models_authenticated(self, auth_client):
        """Model listesi endpoint'i çalışmalı (mock)."""
        with patch("app.services.ai_service.AIService.list_models") as mock:
            from app.schemas.ai import AIModelListResponse

            mock.return_value = AIModelListResponse(models=[])

            resp = await auth_client.get("/api/v1/ai/models")
            assert resp.status_code == 200
            data = resp.json()
            assert data["success"] is True
            assert isinstance(data["data"]["models"], list)

    # ── GET /api/v1/ai/settings ──

    async def test_settings_unauthenticated(self, client):
        """Auth olmadan → 403."""
        resp = await client.get("/api/v1/ai/settings")
        assert resp.status_code == 403

    async def test_settings_authenticated(self, auth_client):
        """AI ayarları endpoint'i çalışmalı."""
        resp = await auth_client.get("/api/v1/ai/settings")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "model" in data["data"]
        assert "temperature" in data["data"]
        assert "api_key_set" in data["data"]

    # ── PUT /api/v1/ai/settings ──

    async def test_update_settings_unauthenticated(self, client):
        """Auth olmadan → 403."""
        resp = await client.put(
            "/api/v1/ai/settings",
            json={"model": "test"},
        )
        assert resp.status_code == 403

    async def test_update_settings_authenticated(self, auth_client):
        """AI ayarları güncelleme."""
        resp = await auth_client.put(
            "/api/v1/ai/settings",
            json={"model": "anthropic/claude-sonnet-4", "temperature": 0.5},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["model"] == "anthropic/claude-sonnet-4"
        assert data["data"]["temperature"] == 0.5

    async def test_update_settings_empty_model(self, auth_client):
        """Boş model → 400."""
        resp = await auth_client.put(
            "/api/v1/ai/settings",
            json={"model": "  "},
        )
        assert resp.status_code == 400
