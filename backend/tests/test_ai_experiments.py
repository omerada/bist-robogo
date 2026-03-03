"""AI Experiment ve Performance testleri — Sprint 3.3.

A/B test deney CRUD, performans metrikleri, şema validasyon,
API endpoint testleri.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

pytestmark = pytest.mark.asyncio(loop_scope="session")


# ═══════════════════════════════════════════════════════════════
# 1. Yeni Şema Testleri
# ═══════════════════════════════════════════════════════════════


class TestAIExperimentSchemas:
    """Sprint 3.3 şema validation testleri."""

    def test_experiment_create_valid(self):
        """AIExperimentCreate geçerli oluşturma."""
        from app.schemas.ai import AIExperimentCreate

        exp = AIExperimentCreate(
            name="Gemini vs GPT",
            model_a="google/gemini-2.5-flash",
            model_b="openai/gpt-4o-mini",
            symbols=["THYAO", "GARAN"],
        )
        assert exp.name == "Gemini vs GPT"
        assert len(exp.symbols) == 2
        assert exp.config == {}
        assert exp.description is None

    def test_experiment_create_empty_name(self):
        """Boş isim → validation error."""
        from pydantic import ValidationError
        from app.schemas.ai import AIExperimentCreate

        with pytest.raises(ValidationError):
            AIExperimentCreate(
                name="",
                model_a="a",
                model_b="b",
                symbols=["THYAO"],
            )

    def test_experiment_create_empty_symbols(self):
        """Boş sembol listesi → validation error."""
        from pydantic import ValidationError
        from app.schemas.ai import AIExperimentCreate

        with pytest.raises(ValidationError):
            AIExperimentCreate(
                name="Test",
                model_a="a",
                model_b="b",
                symbols=[],
            )

    def test_experiment_status_enum(self):
        """AIExperimentStatus enum değerleri."""
        from app.schemas.ai import AIExperimentStatus

        assert AIExperimentStatus.PENDING == "pending"
        assert AIExperimentStatus.RUNNING == "running"
        assert AIExperimentStatus.COMPLETED == "completed"
        assert AIExperimentStatus.FAILED == "failed"

    def test_accuracy_metric_defaults(self):
        """AIAccuracyMetric varsayılan değerleri."""
        from app.schemas.ai import AIAccuracyMetric

        metric = AIAccuracyMetric()
        assert metric.total_analyses == 0
        assert metric.correct_predictions == 0
        assert metric.accuracy_rate == 0.0
        assert metric.buy_accuracy == 0.0

    def test_accuracy_metric_bounds(self):
        """accuracy_rate 0-1 aralığında."""
        from pydantic import ValidationError
        from app.schemas.ai import AIAccuracyMetric

        # Geçerli
        m = AIAccuracyMetric(accuracy_rate=0.85)
        assert m.accuracy_rate == 0.85

        # Geçersiz
        with pytest.raises(ValidationError):
            AIAccuracyMetric(accuracy_rate=1.5)

    def test_model_performance_defaults(self):
        """AIModelPerformance varsayılanları."""
        from app.schemas.ai import AIModelPerformance

        perf = AIModelPerformance(model_id="google/gemini-2.5-flash")
        assert perf.total_analyses == 0
        assert perf.avg_latency_ms == 0.0
        assert perf.avg_score == 0.0
        assert perf.accuracy.accuracy_rate == 0.0

    def test_experiment_response_model(self):
        """AIExperimentResponse oluşturma."""
        from app.schemas.ai import AIExperimentResponse, AIExperimentStatus

        resp = AIExperimentResponse(
            id="test-id",
            user_id="user-id",
            name="Test Deney",
            model_a="google/gemini-2.5-flash",
            model_b="openai/gpt-4o",
            symbols=["THYAO"],
            status=AIExperimentStatus.PENDING,
            created_at=datetime.now(timezone.utc),
        )
        assert resp.name == "Test Deney"
        assert resp.status == "pending"
        assert resp.results == []

    def test_experiment_result_response(self):
        """AIExperimentResultResponse oluşturma."""
        from app.schemas.ai import AIExperimentResultResponse

        r = AIExperimentResultResponse(
            id="res-1",
            experiment_id="exp-1",
            symbol="THYAO",
            model_id="google/gemini-2.5-flash",
            action="buy",
            confidence="high",
            score=0.85,
            latency_ms=450,
            created_at=datetime.now(timezone.utc),
        )
        assert r.score == 0.85
        assert r.action == "buy"

    def test_model_comparison(self):
        """AIModelComparison oluşturma."""
        from app.schemas.ai import AIModelComparison, AIModelPerformance

        comp = AIModelComparison(
            model_a=AIModelPerformance(model_id="model-a"),
            model_b=AIModelPerformance(model_id="model-b"),
            winner="model-a",
            comparison_notes=["Model A daha yüksek doğruluğa sahip"],
        )
        assert comp.winner == "model-a"
        assert len(comp.comparison_notes) == 1

    def test_performance_summary(self):
        """AIPerformanceSummary oluşturma."""
        from app.schemas.ai import AIPerformanceSummary

        summary = AIPerformanceSummary(
            total_analyses=100,
            overall_accuracy=0.72,
            period_days=30,
        )
        assert summary.total_analyses == 100
        assert summary.overall_accuracy == 0.72
        assert summary.models == []

    def test_performance_request_defaults(self):
        """AIPerformanceRequest varsayılanları."""
        from app.schemas.ai import AIPerformanceRequest

        req = AIPerformanceRequest()
        assert req.model_id is None
        assert req.symbol is None
        assert req.days == 30

    def test_performance_request_bounds(self):
        """days 1-365 aralığında."""
        from pydantic import ValidationError
        from app.schemas.ai import AIPerformanceRequest

        # Geçerli
        req = AIPerformanceRequest(days=365)
        assert req.days == 365

        with pytest.raises(ValidationError):
            AIPerformanceRequest(days=0)

        with pytest.raises(ValidationError):
            AIPerformanceRequest(days=400)

    def test_analysis_log_response(self):
        """AIAnalysisLogResponse oluşturma."""
        from app.schemas.ai import AIAnalysisLogResponse

        log = AIAnalysisLogResponse(
            id="log-1",
            symbol="THYAO",
            model_id="google/gemini-2.5-flash",
            action="buy",
            confidence="high",
            score=0.9,
            latency_ms=300,
            created_at=datetime.now(timezone.utc),
        )
        assert log.is_correct is None
        assert log.actual_price_change is None


# ═══════════════════════════════════════════════════════════════
# 2. ORM Model Testleri
# ═══════════════════════════════════════════════════════════════


class TestAIModels:
    """AI ORM model testleri."""

    def test_ai_experiment_repr(self):
        """AIExperiment __repr__."""
        from app.models.ai import AIExperiment

        exp = AIExperiment(name="Test", status="pending")
        assert "Test" in repr(exp)
        assert "pending" in repr(exp)

    def test_ai_experiment_result_repr(self):
        """AIExperimentResult __repr__."""
        from app.models.ai import AIExperimentResult

        r = AIExperimentResult(symbol="THYAO", model_id="test-model", action="buy")
        assert "THYAO" in repr(r)
        assert "buy" in repr(r)

    def test_ai_analysis_log_repr(self):
        """AIAnalysisLog __repr__."""
        from app.models.ai import AIAnalysisLog

        log = AIAnalysisLog(symbol="GARAN", model_id="test", action="sell")
        assert "GARAN" in repr(log)
        assert "sell" in repr(log)

    def test_ai_experiment_table_name(self):
        """Tablo adı kontrolü."""
        from app.models.ai import AIExperiment

        assert AIExperiment.__tablename__ == "ai_experiments"

    def test_ai_experiment_result_table_name(self):
        from app.models.ai import AIExperimentResult

        assert AIExperimentResult.__tablename__ == "ai_experiment_results"

    def test_ai_analysis_log_table_name(self):
        from app.models.ai import AIAnalysisLog

        assert AIAnalysisLog.__tablename__ == "ai_analysis_logs"


# ═══════════════════════════════════════════════════════════════
# 3. API Endpoint Testleri
# ═══════════════════════════════════════════════════════════════


class TestExperimentAPI:
    """A/B test deney API endpoint testleri."""

    # ── POST /api/v1/ai/experiments ──

    async def test_create_experiment_unauthenticated(self, client):
        """Auth olmadan → 403."""
        resp = await client.post(
            "/api/v1/ai/experiments",
            json={
                "name": "Test",
                "model_a": "a",
                "model_b": "b",
                "symbols": ["THYAO"],
            },
        )
        assert resp.status_code == 403

    async def test_create_experiment_authenticated(self, auth_client):
        """Deney oluşturma (mock service)."""
        with patch(
            "app.services.ai_experiment_service.AIExperimentService.create_experiment"
        ) as mock:
            from app.schemas.ai import AIExperimentResponse, AIExperimentStatus

            mock.return_value = AIExperimentResponse(
                id="exp-1",
                user_id="user-1",
                name="Test Deney",
                model_a="google/gemini-2.5-flash",
                model_b="openai/gpt-4o",
                symbols=["THYAO"],
                status=AIExperimentStatus.PENDING,
                created_at=datetime.now(timezone.utc),
            )

            resp = await auth_client.post(
                "/api/v1/ai/experiments",
                json={
                    "name": "Test Deney",
                    "model_a": "google/gemini-2.5-flash",
                    "model_b": "openai/gpt-4o",
                    "symbols": ["THYAO"],
                },
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["success"] is True
            assert data["data"]["name"] == "Test Deney"

    # ── GET /api/v1/ai/experiments ──

    async def test_list_experiments_unauthenticated(self, client):
        """Auth olmadan → 403."""
        resp = await client.get("/api/v1/ai/experiments")
        assert resp.status_code == 403

    async def test_list_experiments_authenticated(self, auth_client):
        """Deney listesi (mock)."""
        with patch(
            "app.services.ai_experiment_service.AIExperimentService.list_experiments"
        ) as mock:
            mock.return_value = ([], 0)

            resp = await auth_client.get("/api/v1/ai/experiments")
            assert resp.status_code == 200
            data = resp.json()
            assert data["success"] is True
            assert data["data"]["total"] == 0

    # ── GET /api/v1/ai/experiments/{id} ──

    async def test_get_experiment_not_found(self, auth_client):
        """Olmayan deney → 404."""
        with patch(
            "app.services.ai_experiment_service.AIExperimentService.get_experiment"
        ) as mock:
            mock.return_value = None

            resp = await auth_client.get(
                "/api/v1/ai/experiments/00000000-0000-0000-0000-000000000001"
            )
            assert resp.status_code == 404

    # ── DELETE /api/v1/ai/experiments/{id} ──

    async def test_delete_experiment_unauthenticated(self, client):
        """Auth olmadan → 403."""
        resp = await client.delete(
            "/api/v1/ai/experiments/00000000-0000-0000-0000-000000000001"
        )
        assert resp.status_code == 403

    async def test_delete_experiment_not_found(self, auth_client):
        """Olmayan deney → 404."""
        with patch(
            "app.services.ai_experiment_service.AIExperimentService.delete_experiment"
        ) as mock:
            mock.return_value = False

            resp = await auth_client.delete(
                "/api/v1/ai/experiments/00000000-0000-0000-0000-000000000001"
            )
            assert resp.status_code == 404

    async def test_delete_experiment_success(self, auth_client):
        """Başarılı silme → 204."""
        with patch(
            "app.services.ai_experiment_service.AIExperimentService.delete_experiment"
        ) as mock:
            mock.return_value = True

            resp = await auth_client.delete(
                "/api/v1/ai/experiments/00000000-0000-0000-0000-000000000001"
            )
            assert resp.status_code == 204


class TestPerformanceAPI:
    """AI performans API endpoint testleri."""

    # ── GET /api/v1/ai/performance ──

    async def test_performance_unauthenticated(self, client):
        """Auth olmadan → 403."""
        resp = await client.get("/api/v1/ai/performance")
        assert resp.status_code == 403

    async def test_performance_authenticated(self, auth_client):
        """Performans özeti (mock)."""
        with patch(
            "app.services.ai_experiment_service.AIExperimentService.get_model_performance"
        ) as mock:
            from app.schemas.ai import AIPerformanceSummary

            mock.return_value = AIPerformanceSummary(
                total_analyses=50,
                overall_accuracy=0.7,
                period_days=30,
            )

            resp = await auth_client.get("/api/v1/ai/performance")
            assert resp.status_code == 200
            data = resp.json()
            assert data["success"] is True
            assert data["data"]["total_analyses"] == 50

    async def test_performance_with_params(self, auth_client):
        """Filtreli performans sorgusu."""
        with patch(
            "app.services.ai_experiment_service.AIExperimentService.get_model_performance"
        ) as mock:
            from app.schemas.ai import AIPerformanceSummary

            mock.return_value = AIPerformanceSummary(
                total_analyses=10,
                overall_accuracy=0.8,
                period_days=7,
            )

            resp = await auth_client.get(
                "/api/v1/ai/performance",
                params={"model_id": "google/gemini-2.5-flash", "days": 7},
            )
            assert resp.status_code == 200
            mock.assert_called_once()

    # ── GET /api/v1/ai/performance/compare ──

    async def test_compare_unauthenticated(self, client):
        """Auth olmadan → 403."""
        resp = await client.get(
            "/api/v1/ai/performance/compare",
            params={"model_a": "a", "model_b": "b"},
        )
        assert resp.status_code == 403

    async def test_compare_authenticated(self, auth_client):
        """Model karşılaştırma (mock)."""
        with patch(
            "app.services.ai_experiment_service.AIExperimentService.get_model_comparison"
        ) as mock:
            from app.schemas.ai import (
                AIModelComparison,
                AIModelComparisonResponse,
                AIModelPerformance,
            )

            mock.return_value = AIModelComparisonResponse(
                comparison=AIModelComparison(
                    model_a=AIModelPerformance(model_id="model-a"),
                    model_b=AIModelPerformance(model_id="model-b"),
                    winner="model-a",
                    comparison_notes=["Model A daha iyi"],
                )
            )

            resp = await auth_client.get(
                "/api/v1/ai/performance/compare",
                params={"model_a": "model-a", "model_b": "model-b"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["success"] is True
            assert data["data"]["comparison"]["winner"] == "model-a"

    async def test_compare_missing_params(self, auth_client):
        """Eksik parametre → 422."""
        resp = await auth_client.get(
            "/api/v1/ai/performance/compare",
            params={"model_a": "a"},
        )
        assert resp.status_code == 422
