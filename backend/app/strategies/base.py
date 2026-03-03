"""Strateji abstract base class — tüm stratejiler bunu implement eder."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

import pandas as pd


class SignalType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass
class StrategySignal:
    """Strateji tarafından üretilen sinyal."""

    symbol: str
    signal_type: SignalType
    confidence: float  # 0.0 - 1.0
    target_price: Decimal | None = None
    stop_loss: Decimal | None = None
    take_profit: Decimal | None = None
    reason: str = ""
    metadata: dict | None = None


class BaseStrategy(ABC):
    """Tüm ticaret stratejilerinin temel sınıfı.

    Her strateji şunları implement etmelidir:
    1. analyze() — Veriyi analiz et ve sinyal üret
    2. name — Strateji adı (benzersiz)
    3. description — Strateji açıklaması
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Strateji benzersiz adı."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Strateji açıklaması."""
        pass

    @abstractmethod
    async def analyze(
        self,
        symbol: str,
        ohlcv: pd.DataFrame,
        params: dict | None = None,
    ) -> StrategySignal:
        """Veriyi analiz et ve al/sat/tut sinyali üret.

        Args:
            symbol: Hisse sembolü
            ohlcv: OHLCV verileri (open, high, low, close, volume kolonları)
            params: Strateji parametreleri (override)

        Returns:
            StrategySignal
        """
        pass

    def validate_params(self, params: dict) -> dict:
        """Strateji parametrelerini doğrula. Alt sınıflar override edebilir."""
        return params
