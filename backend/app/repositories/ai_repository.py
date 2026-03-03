# Source: Doc 10 §Faz 3 Sprint 3.3 — AI deney ve performans repository
"""AI deneyleri, sonuçları ve analiz logları veritabanı erişim katmanı."""

import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import Integer, func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai import AIAnalysisLog, AIExperiment, AIExperimentResult
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class AIExperimentRepository(BaseRepository[AIExperiment]):
    """A/B test deneyi CRUD + özel sorgular."""

    def __init__(self, db: AsyncSession):
        super().__init__(AIExperiment, db)

    async def get_by_user(
        self,
        user_id: UUID,
        status: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[AIExperiment]:
        """Kullanıcının deneylerini listele."""
        stmt = select(AIExperiment).where(AIExperiment.user_id == user_id)

        if status:
            stmt = stmt.where(AIExperiment.status == status)

        stmt = stmt.order_by(AIExperiment.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_user(
        self,
        user_id: UUID,
        status: str | None = None,
    ) -> int:
        """Kullanıcının deney sayısı."""
        stmt = (
            select(func.count())
            .select_from(AIExperiment)
            .where(AIExperiment.user_id == user_id)
        )
        if status:
            stmt = stmt.where(AIExperiment.status == status)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_user_experiment(
        self, experiment_id: UUID, user_id: UUID
    ) -> AIExperiment | None:
        """Kullanıcıya ait deneyi getir."""
        stmt = select(AIExperiment).where(
            AIExperiment.id == experiment_id, AIExperiment.user_id == user_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class AIExperimentResultRepository(BaseRepository[AIExperimentResult]):
    """Deney sonuçları repository."""

    def __init__(self, db: AsyncSession):
        super().__init__(AIExperimentResult, db)

    async def get_by_experiment(
        self,
        experiment_id: UUID,
        model_id: str | None = None,
    ) -> list[AIExperimentResult]:
        """Deneyin sonuçlarını listele."""
        stmt = select(AIExperimentResult).where(
            AIExperimentResult.experiment_id == experiment_id
        )
        if model_id:
            stmt = stmt.where(AIExperimentResult.model_id == model_id)
        stmt = stmt.order_by(AIExperimentResult.created_at.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_bulk(self, results: list[dict]) -> list[AIExperimentResult]:
        """Toplu sonuç kaydet."""
        instances = [AIExperimentResult(**r) for r in results]
        self.db.add_all(instances)
        await self.db.flush()
        return instances

    async def get_avg_metrics_by_model(
        self, experiment_id: UUID
    ) -> list[dict]:
        """Model bazında ortalama metrikler."""
        stmt = (
            select(
                AIExperimentResult.model_id,
                func.count().label("total"),
                func.avg(AIExperimentResult.score).label("avg_score"),
                func.avg(AIExperimentResult.latency_ms).label("avg_latency"),
            )
            .where(AIExperimentResult.experiment_id == experiment_id)
            .group_by(AIExperimentResult.model_id)
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        return [
            {
                "model_id": r.model_id,
                "total": r.total,
                "avg_score": float(r.avg_score or 0),
                "avg_latency": float(r.avg_latency or 0),
            }
            for r in rows
        ]


class AIAnalysisLogRepository(BaseRepository[AIAnalysisLog]):
    """AI analiz log repository — performans takibi için."""

    def __init__(self, db: AsyncSession):
        super().__init__(AIAnalysisLog, db)

    async def log_analysis(
        self,
        symbol: str,
        model_id: str,
        action: str,
        confidence: str,
        score: float,
        latency_ms: int = 0,
        token_usage: dict | None = None,
        user_id: UUID | None = None,
        metadata: dict | None = None,
    ) -> AIAnalysisLog:
        """Yeni analiz logu oluştur."""
        log = AIAnalysisLog(
            user_id=user_id,
            symbol=symbol,
            model_id=model_id,
            action=action,
            confidence=confidence,
            score=score,
            latency_ms=latency_ms,
            token_usage=token_usage or {},
            metadata_=metadata or {},
        )
        self.db.add(log)
        await self.db.flush()
        return log

    async def get_model_performance(
        self,
        model_id: str | None = None,
        symbol: str | None = None,
        days: int = 30,
    ) -> list[dict]:
        """Model performans metriklerini hesapla."""
        since = datetime.now(timezone.utc) - timedelta(days=days)
        filters = [AIAnalysisLog.created_at >= since]
        if model_id:
            filters.append(AIAnalysisLog.model_id == model_id)
        if symbol:
            filters.append(AIAnalysisLog.symbol == symbol)

        stmt = (
            select(
                AIAnalysisLog.model_id,
                func.count().label("total_analyses"),
                func.avg(AIAnalysisLog.latency_ms).label("avg_latency_ms"),
                func.avg(AIAnalysisLog.score).label("avg_score"),
                func.sum(
                    func.cast(AIAnalysisLog.is_correct == True, Integer)  # noqa: E712
                ).label("correct_count"),
            )
            .where(and_(*filters))
            .group_by(AIAnalysisLog.model_id)
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        perfs = []
        for r in rows:
            total = r.total_analyses or 0
            correct = r.correct_count or 0
            perfs.append(
                {
                    "model_id": r.model_id,
                    "total_analyses": total,
                    "avg_latency_ms": float(r.avg_latency_ms or 0),
                    "avg_score": float(r.avg_score or 0),
                    "correct_predictions": correct,
                    "accuracy_rate": correct / total if total > 0 else 0.0,
                }
            )
        return perfs

    async def get_accuracy_by_action(
        self,
        model_id: str,
        days: int = 30,
    ) -> dict:
        """Aksiyon bazında doğruluk oranları."""
        since = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = (
            select(
                AIAnalysisLog.action,
                func.count().label("total"),
                func.sum(
                    func.cast(AIAnalysisLog.is_correct == True, Integer)  # noqa: E712
                ).label("correct"),
            )
            .where(
                and_(
                    AIAnalysisLog.model_id == model_id,
                    AIAnalysisLog.created_at >= since,
                    AIAnalysisLog.is_correct.isnot(None),
                )
            )
            .group_by(AIAnalysisLog.action)
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        accuracy = {}
        for r in rows:
            total = r.total or 0
            correct = r.correct or 0
            accuracy[r.action] = correct / total if total > 0 else 0.0
        return accuracy

    async def get_recent_logs(
        self,
        model_id: str | None = None,
        symbol: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[AIAnalysisLog]:
        """Son analiz loglarını getir."""
        stmt = select(AIAnalysisLog)
        if model_id:
            stmt = stmt.where(AIAnalysisLog.model_id == model_id)
        if symbol:
            stmt = stmt.where(AIAnalysisLog.symbol == symbol)
        stmt = stmt.order_by(AIAnalysisLog.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
