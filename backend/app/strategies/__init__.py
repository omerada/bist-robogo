"""Strateji modülü — tüm strateji implementasyonlarını dışa aktarır."""

from app.strategies.base import BaseStrategy, SignalType, StrategySignal
from app.strategies.ma_crossover import MACrossoverStrategy
from app.strategies.rsi_reversal import RSIReversalStrategy

# Kayıtlı strateji tipleri
STRATEGY_REGISTRY: dict[str, type[BaseStrategy]] = {
    "ma_crossover": MACrossoverStrategy,
    "rsi_reversal": RSIReversalStrategy,
}

__all__ = [
    "BaseStrategy",
    "SignalType",
    "StrategySignal",
    "MACrossoverStrategy",
    "RSIReversalStrategy",
    "STRATEGY_REGISTRY",
]
