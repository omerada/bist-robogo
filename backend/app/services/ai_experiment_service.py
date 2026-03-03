# Source: Doc 10 §Faz 3 Sprint 3.3 — AI deney ve performans servisi
"""AI A/B test deney yönetimi ve performans karşılaştırma servisi."""

import logging
import time
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.openrouter_client import OpenRouterClient, OpenRouterError
from app.repositories.ai_repository import (
    AIAnalysisLogRepository,
    AIExperimentRepository,
    AIExperimentResultRepository,
)
from app.schemas.ai import (
    AIAccuracyMetric,
    AIExperimentCreate,
    AIExperimentResponse,
    AIExperimentResultResponse,
    AIExperimentStatus,
    AIModelComparison,
    AIModelComparisonResponse,
    AIModelPerformance,
    AIPerformanceSummary,
    AISignalAction,
    AIConfidence,
)

logger = logging.getLogger(__name__)

# A/B test için analiz prompt'u
_AB_ANALYSIS_PROMPT = """Sen BIST teknik analiz uzmanısın.
Verilen sembolü analiz et, JSON formatında yanıt ver:
{{"action": "buy"|"sell"|"hold", "confidence": "low"|"medium"|"high", "score": 0.0-1.0, "reasoning": "Kısa gerekçe"}}"""


class AIExperimentService:
    """A/B test deneyleri yönetimi ve model performans karşılaştırma."""

    def __init__(self, db: AsyncSession, client: OpenRouterClient | None = None):
        self.db = db
        self.client = client or OpenRouterClient()
        self.experiment_repo = AIExperimentRepository(db)
        self.result_repo = AIExperimentResultRepository(db)
        self.log_repo = AIAnalysisLogRepository(db)

    # ── Deney CRUD ──

    async def create_experiment(
        self, user_id: UUID, data: AIExperimentCreate
    ) -> AIExperimentResponse:
        """Yeni A/B test deneyi oluştur."""
        experiment = await self.experiment_repo.create(
            user_id=user_id,
            name=data.name,
            description=data.description,
            model_a=data.model_a,
            model_b=data.model_b,
            symbols=data.symbols,
            config=data.config,
            status="pending",
        )
        await self.db.commit()
        return self._to_experiment_response(experiment)

    async def get_experiment(
        self, experiment_id: UUID, user_id: UUID
    ) -> AIExperimentResponse | None:
        """Kullanıcıya ait deneyi getir."""
        experiment = await self.experiment_repo.get_user_experiment(
            experiment_id, user_id
        )
        if not experiment:
            return None

        results = await self.result_repo.get_by_experiment(experiment.id)
        return self._to_experiment_response(experiment, results)

    async def list_experiments(
        self,
        user_id: UUID,
        status: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[AIExperimentResponse], int]:
        """Kullanıcının deneylerini listele."""
        experiments = await self.experiment_repo.get_by_user(
            user_id, status=status, skip=skip, limit=limit
        )
        total = await self.experiment_repo.count_by_user(user_id, status=status)
        return [self._to_experiment_response(e) for e in experiments], total

    async def delete_experiment(
        self, experiment_id: UUID, user_id: UUID
    ) -> bool:
        """Deneyi sil."""
        experiment = await self.experiment_repo.get_user_experiment(
            experiment_id, user_id
        )
        if not experiment:
            return False
        await self.experiment_repo.delete(experiment)
        await self.db.commit()
        return True

    # ── Deney Çalıştırma ──

    async def run_experiment(
        self, experiment_id: UUID, user_id: UUID
    ) -> AIExperimentResponse | None:
        """A/B test deneyini çalıştır — her sembol için iki modelden analiz al."""
        experiment = await self.experiment_repo.get_user_experiment(
            experiment_id, user_id
        )
        if not experiment:
            return None

        if experiment.status not in ("pending", "failed"):
            logger.warning(
                "Deney %s zaten %s durumunda", experiment_id, experiment.status
            )
            return self._to_experiment_response(experiment)

        # Running durumuna geçir
        await self.experiment_repo.update(
            experiment,
            status="running",
            started_at=datetime.now(timezone.utc),
        )
        await self.db.commit()

        try:
            results_data = []
            for symbol in experiment.symbols:
                # Model A analizi
                result_a = await self._run_single_analysis(
                    symbol, experiment.model_a, experiment.config
                )
                result_a["experiment_id"] = experiment.id
                results_data.append(result_a)

                # Model B analizi
                result_b = await self._run_single_analysis(
                    symbol, experiment.model_b, experiment.config
                )
                result_b["experiment_id"] = experiment.id
                results_data.append(result_b)

            # Toplu kaydet
            await self.result_repo.create_bulk(results_data)

            # Tamamlandı
            await self.experiment_repo.update(
                experiment,
                status="completed",
                completed_at=datetime.now(timezone.utc),
            )
            await self.db.commit()

        except Exception as exc:
            logger.error("Deney çalıştırma hatası %s: %s", experiment_id, exc)
            await self.experiment_repo.update(experiment, status="failed")
            await self.db.commit()

        # Sonuçlarla birlikte döndür
        results = await self.result_repo.get_by_experiment(experiment.id)
        return self._to_experiment_response(experiment, results)

    async def _run_single_analysis(
        self, symbol: str, model_id: str, config: dict
    ) -> dict:
        """Tek sembol + tek model analizi çalıştır."""
        prompt = f"{symbol} hissesini analiz et."
        start = time.monotonic()

        try:
            # Geçici olarak modeli değiştir
            original_model = self.client.model
            self.client.model = model_id

            result = await self.client.get_json(
                messages=[
                    {"role": "system", "content": _AB_ANALYSIS_PROMPT},
                    {"role": "user", "content": prompt},
                ]
            )
            self.client.model = original_model
        except OpenRouterError:
            result = {
                "action": "hold",
                "confidence": "low",
                "score": 0.0,
                "reasoning": "AI yanıtı alınamadı",
            }

        latency = int((time.monotonic() - start) * 1000)

        return {
            "symbol": symbol,
            "model_id": model_id,
            "action": result.get("action", "hold"),
            "confidence": result.get("confidence", "low"),
            "score": float(result.get("score", 0.0)),
            "reasoning": result.get("reasoning", ""),
            "latency_ms": latency,
            "token_usage": result.get("usage", {}),
        }

    # ── Performans Metrikleri ──

    async def get_model_performance(
        self,
        model_id: str | None = None,
        symbol: str | None = None,
        days: int = 30,
    ) -> AIPerformanceSummary:
        """Model performans özetini hesapla."""
        perf_rows = await self.log_repo.get_model_performance(
            model_id=model_id, symbol=symbol, days=days
        )
        models = []
        total_analyses = 0
        all_correct = 0
        all_total = 0

        for row in perf_rows:
            # Aksiyon bazında doğruluk
            action_accuracy = await self.log_repo.get_accuracy_by_action(
                row["model_id"], days=days
            )
            accuracy = AIAccuracyMetric(
                total_analyses=row["total_analyses"],
                correct_predictions=row["correct_predictions"],
                accuracy_rate=row["accuracy_rate"],
                buy_accuracy=action_accuracy.get("buy", 0.0),
                sell_accuracy=action_accuracy.get("sell", 0.0),
                hold_accuracy=action_accuracy.get("hold", 0.0),
            )
            models.append(
                AIModelPerformance(
                    model_id=row["model_id"],
                    total_analyses=row["total_analyses"],
                    avg_latency_ms=row["avg_latency_ms"],
                    avg_score=row["avg_score"],
                    accuracy=accuracy,
                )
            )
            total_analyses += row["total_analyses"]
            all_correct += row["correct_predictions"]
            all_total += row["total_analyses"]

        return AIPerformanceSummary(
            models=models,
            total_analyses=total_analyses,
            overall_accuracy=all_correct / all_total if all_total > 0 else 0.0,
            period_days=days,
        )

    async def get_model_comparison(
        self, model_a_id: str, model_b_id: str, days: int = 30
    ) -> AIModelComparisonResponse:
        """İki modeli karşılaştır."""
        perf_a = await self._get_single_model_perf(model_a_id, days)
        perf_b = await self._get_single_model_perf(model_b_id, days)

        # Kazanan belirleme
        notes = []
        winner = None
        if perf_a.accuracy.accuracy_rate > perf_b.accuracy.accuracy_rate:
            winner = model_a_id
            notes.append(
                f"{model_a_id} daha yüksek doğruluk oranına sahip "
                f"({perf_a.accuracy.accuracy_rate:.1%} vs {perf_b.accuracy.accuracy_rate:.1%})"
            )
        elif perf_b.accuracy.accuracy_rate > perf_a.accuracy.accuracy_rate:
            winner = model_b_id
            notes.append(
                f"{model_b_id} daha yüksek doğruluk oranına sahip "
                f"({perf_b.accuracy.accuracy_rate:.1%} vs {perf_a.accuracy.accuracy_rate:.1%})"
            )

        if perf_a.avg_latency_ms < perf_b.avg_latency_ms:
            notes.append(f"{model_a_id} daha hızlı ({perf_a.avg_latency_ms:.0f}ms vs {perf_b.avg_latency_ms:.0f}ms)")
        elif perf_b.avg_latency_ms < perf_a.avg_latency_ms:
            notes.append(f"{model_b_id} daha hızlı ({perf_b.avg_latency_ms:.0f}ms vs {perf_a.avg_latency_ms:.0f}ms)")

        return AIModelComparisonResponse(
            comparison=AIModelComparison(
                model_a=perf_a,
                model_b=perf_b,
                winner=winner,
                comparison_notes=notes,
            )
        )

    async def _get_single_model_perf(
        self, model_id: str, days: int
    ) -> AIModelPerformance:
        """Tek model performans verisi."""
        rows = await self.log_repo.get_model_performance(
            model_id=model_id, days=days
        )
        if not rows:
            return AIModelPerformance(model_id=model_id)

        row = rows[0]
        action_accuracy = await self.log_repo.get_accuracy_by_action(model_id, days)
        return AIModelPerformance(
            model_id=model_id,
            total_analyses=row["total_analyses"],
            avg_latency_ms=row["avg_latency_ms"],
            avg_score=row["avg_score"],
            accuracy=AIAccuracyMetric(
                total_analyses=row["total_analyses"],
                correct_predictions=row["correct_predictions"],
                accuracy_rate=row["accuracy_rate"],
                buy_accuracy=action_accuracy.get("buy", 0.0),
                sell_accuracy=action_accuracy.get("sell", 0.0),
                hold_accuracy=action_accuracy.get("hold", 0.0),
            ),
        )

    # ── Yardımcı ──

    def _to_experiment_response(
        self, exp, results=None
    ) -> AIExperimentResponse:
        """ORM → Pydantic dönüşümü."""
        result_items = []
        if results:
            for r in results:
                result_items.append(
                    AIExperimentResultResponse(
                        id=str(r.id),
                        experiment_id=str(r.experiment_id),
                        symbol=r.symbol,
                        model_id=r.model_id,
                        action=AISignalAction(r.action),
                        confidence=AIConfidence(r.confidence),
                        score=float(r.score),
                        reasoning=r.reasoning,
                        latency_ms=r.latency_ms,
                        token_usage=r.token_usage or {},
                        created_at=r.created_at,
                    )
                )

        return AIExperimentResponse(
            id=str(exp.id),
            user_id=str(exp.user_id),
            name=exp.name,
            description=exp.description,
            model_a=exp.model_a,
            model_b=exp.model_b,
            symbols=exp.symbols or [],
            status=AIExperimentStatus(exp.status),
            config=exp.config or {},
            started_at=exp.started_at,
            completed_at=exp.completed_at,
            created_at=exp.created_at,
            updated_at=exp.updated_at,
            results=result_items,
        )
