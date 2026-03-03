# Source: Doc 02 §2.7 — Backtest Engine
"""Backtest iş mantığı — strateji simülasyonu, performans metrikleri."""

import logging
import math
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID

import numpy as np
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.backtest import BacktestRun
from app.repositories.backtest_repository import (
    BacktestRunRepository,
    BacktestTradeRepository,
)
from app.repositories.market_repository import OHLCVRepository, SymbolRepository
from app.repositories.strategy_repository import StrategyRepository
from app.schemas.backtest import (
    BacktestDetailResponse,
    BacktestResultResponse,
    BacktestRunRequest,
    BacktestTradeResponse,
)
from app.strategies import STRATEGY_REGISTRY

logger = logging.getLogger(__name__)


class BacktestService:
    """Backtest iş mantığı — simülasyon çalıştırma, sonuç sorgulama."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.backtest_repo = BacktestRunRepository(db)
        self.trade_repo = BacktestTradeRepository(db)
        self.strategy_repo = StrategyRepository(db)
        self.ohlcv_repo = OHLCVRepository(db)
        self.symbol_repo = SymbolRepository(db)

    # ── Backtest Oluşturma ──

    async def create_backtest(
        self,
        user_id: UUID,
        data: BacktestRunRequest,
    ) -> BacktestResultResponse:
        """Yeni backtest kaydı oluştur (pending durumda)."""
        # Strateji kontrolü
        strategy = await self.strategy_repo.get_by_id(data.strategy_id)
        if not strategy:
            raise ValueError("Strateji bulunamadı")
        if strategy.user_id != user_id:
            raise ValueError("Bu strateji size ait değil")

        # Tarih kontrolü
        if data.start_date >= data.end_date:
            raise ValueError("Başlangıç tarihi bitiş tarihinden önce olmalı")

        backtest = await self.backtest_repo.create(
            user_id=user_id,
            strategy_id=data.strategy_id,
            name=data.name or f"{strategy.name} Backtest",
            parameters=data.parameters or strategy.parameters,
            symbols=data.symbols,
            start_date=data.start_date,
            end_date=data.end_date,
            initial_capital=float(data.initial_capital),
            commission_rate=float(data.commission_rate),
            slippage_rate=float(data.slippage_rate),
            status="pending",
        )
        await self.db.commit()
        await self.db.refresh(backtest)
        logger.info(f"Backtest oluşturuldu: {backtest.id}")
        return BacktestResultResponse.model_validate(backtest)

    # ── Backtest Çalıştırma ──

    async def run_backtest(self, backtest_id: UUID) -> BacktestResultResponse:
        """Backtest simülasyonunu çalıştır."""
        backtest = await self.backtest_repo.get_by_id(backtest_id)
        if not backtest:
            raise ValueError("Backtest bulunamadı")

        # ORM attribute'larını commit öncesi yerel değişkenlere kopyala
        # (async SQLAlchemy'de commit sonrası lazy-load MissingGreenlet hatası verir)
        bt_id = backtest.id
        bt_strategy_id = backtest.strategy_id
        bt_symbols = list(backtest.symbols)
        bt_parameters = dict(backtest.parameters)
        bt_start_date = backtest.start_date
        bt_end_date = backtest.end_date
        bt_initial_capital = float(backtest.initial_capital)
        bt_commission_rate = float(backtest.commission_rate)
        bt_slippage_rate = float(backtest.slippage_rate)

        # Durumu running yap
        await self.backtest_repo.update_status(
            bt_id, "running", started_at=datetime.now(timezone.utc)
        )
        await self.db.commit()

        try:
            # Strateji tipi al
            strategy = await self.strategy_repo.get_by_id(bt_strategy_id)
            if not strategy:
                raise ValueError("Strateji bulunamadı")

            strategy_type = strategy.strategy_type
            if strategy_type not in STRATEGY_REGISTRY:
                raise ValueError(f"Bilinmeyen strateji tipi: {strategy_type}")

            strategy_instance = STRATEGY_REGISTRY[strategy_type]()

            # Her sembol için simülasyon
            all_trades = []
            all_equity_points = []

            for symbol in bt_symbols:
                ohlcv_data = await self._get_ohlcv_dataframe(
                    symbol, bt_start_date, bt_end_date
                )
                if ohlcv_data.empty or len(ohlcv_data) < 50:
                    logger.warning(f"Yetersiz veri: {symbol}")
                    continue

                trades, equity_points = await self._simulate_symbol(
                    strategy_instance=strategy_instance,
                    symbol=symbol,
                    ohlcv=ohlcv_data,
                    params=bt_parameters,
                    initial_capital=bt_initial_capital / len(bt_symbols),
                    commission_rate=bt_commission_rate,
                    slippage_rate=bt_slippage_rate,
                )
                all_trades.extend(trades)
                all_equity_points.extend(equity_points)

            # Trade'leri kaydet
            if all_trades:
                trade_dicts = [
                    {**t, "backtest_id": bt_id} for t in all_trades
                ]
                await self.trade_repo.bulk_create(trade_dicts)

            # Performans metrikleri hesapla
            metrics = self._calculate_metrics(
                trades=all_trades,
                equity_points=all_equity_points,
                initial_capital=bt_initial_capital,
                start_date=bt_start_date,
                end_date=bt_end_date,
            )

            # Equity curve oluştur
            equity_curve = self._build_equity_curve(
                all_equity_points, bt_initial_capital
            )

            # Sonuçları güncelle
            await self.backtest_repo.update_status(
                bt_id,
                "completed",
                completed_at=datetime.now(timezone.utc),
                total_return=metrics["total_return"],
                cagr=metrics["cagr"],
                sharpe_ratio=metrics["sharpe_ratio"],
                sortino_ratio=metrics["sortino_ratio"],
                max_drawdown=metrics["max_drawdown"],
                win_rate=metrics["win_rate"],
                profit_factor=metrics["profit_factor"],
                total_trades=metrics["total_trades"],
                avg_trade_pnl=metrics["avg_trade_pnl"],
                avg_holding_days=metrics["avg_holding_days"],
                equity_curve=equity_curve,
            )
            await self.db.commit()

            # Güncel nesneyi veritabanından tekrar yükle
            updated = await self.backtest_repo.get_by_id(bt_id)
            logger.info(
                f"Backtest tamamlandı: {bt_id}, "
                f"trades={metrics['total_trades']}, "
                f"return={metrics['total_return']}"
            )
            return BacktestResultResponse.model_validate(updated)

        except Exception as exc:
            logger.error(f"Backtest hatası: {backtest_id} — {exc}")
            await self.backtest_repo.update_status(
                bt_id,
                "failed",
                completed_at=datetime.now(timezone.utc),
                error_message=str(exc),
            )
            await self.db.commit()

            failed = await self.backtest_repo.get_by_id(bt_id)
            return BacktestResultResponse.model_validate(failed)

    # ── Simülasyon ──

    async def _simulate_symbol(
        self,
        strategy_instance,
        symbol: str,
        ohlcv: pd.DataFrame,
        params: dict,
        initial_capital: float,
        commission_rate: float,
        slippage_rate: float,
    ) -> tuple[list[dict], list[dict]]:
        """Tek sembol için backtest simülasyonu.

        Returns:
            (trades, equity_points) tuple'ı
        """
        trades: list[dict] = []
        equity_points: list[dict] = []
        cash = initial_capital
        position_qty = 0
        position_avg_price = 0.0
        entry_date = None

        # Minimum lookback periyodu (50 bar)
        lookback = 50

        for i in range(lookback, len(ohlcv)):
            window = ohlcv.iloc[: i + 1].copy()
            current_bar = ohlcv.iloc[i]
            current_date = current_bar["time"]
            current_price = current_bar["close"]

            # Strateji sinyali al
            try:
                signal = await strategy_instance.analyze(
                    symbol=symbol, ohlcv=window, params=params
                )
            except Exception:
                continue

            # Sinyal işleme
            if signal.signal_type.value == "buy" and position_qty == 0:
                # Alış — slippage uygula
                buy_price = current_price * (1 + slippage_rate)
                # Komisyon dahil maliyet
                max_qty = int(cash / (buy_price * (1 + commission_rate)))
                if max_qty <= 0:
                    continue

                qty = max_qty
                cost = qty * buy_price
                commission = cost * commission_rate
                cash -= cost + commission
                position_qty = qty
                position_avg_price = buy_price
                entry_date = current_date

            elif signal.signal_type.value == "sell" and position_qty > 0:
                # Satış — slippage uygula
                sell_price = current_price * (1 - slippage_rate)
                revenue = position_qty * sell_price
                commission = revenue * commission_rate
                cash += revenue - commission

                # Trade kaydı
                pnl = (sell_price - position_avg_price) * position_qty - (
                    commission + position_avg_price * position_qty * commission_rate
                )
                pnl_pct = (
                    (sell_price - position_avg_price) / position_avg_price * 100
                    if position_avg_price > 0
                    else 0
                )
                holding = (
                    (pd.Timestamp(current_date) - pd.Timestamp(entry_date)).days
                    if entry_date
                    else 0
                )

                trades.append(
                    {
                        "symbol": symbol,
                        "side": "long",
                        "entry_date": entry_date if isinstance(entry_date, date) else pd.Timestamp(entry_date).date(),
                        "entry_price": round(position_avg_price, 4),
                        "exit_date": current_date if isinstance(current_date, date) else pd.Timestamp(current_date).date(),
                        "exit_price": round(sell_price, 4),
                        "quantity": position_qty,
                        "pnl": round(pnl, 4),
                        "pnl_pct": round(pnl_pct, 4),
                        "holding_days": holding,
                        "signal_metadata": {
                            "confidence": signal.confidence,
                            "reason": signal.reason,
                        },
                    }
                )

                position_qty = 0
                position_avg_price = 0.0
                entry_date = None

            # Equity point (günlük)
            portfolio_value = cash + position_qty * current_price
            equity_points.append(
                {
                    "date": str(current_date) if not isinstance(current_date, str) else current_date,
                    "value": round(portfolio_value, 2),
                    "symbol": symbol,
                }
            )

        # Açık pozisyon varsa son fiyattan kapat
        if position_qty > 0:
            last_price = ohlcv.iloc[-1]["close"]
            sell_price = last_price * (1 - slippage_rate)
            revenue = position_qty * sell_price
            commission = revenue * commission_rate
            cash += revenue - commission

            pnl = (sell_price - position_avg_price) * position_qty - (
                commission + position_avg_price * position_qty * commission_rate
            )
            pnl_pct = (
                (sell_price - position_avg_price) / position_avg_price * 100
                if position_avg_price > 0
                else 0
            )
            last_date = ohlcv.iloc[-1]["time"]
            holding = (
                (pd.Timestamp(last_date) - pd.Timestamp(entry_date)).days
                if entry_date
                else 0
            )

            trades.append(
                {
                    "symbol": symbol,
                    "side": "long",
                    "entry_date": entry_date if isinstance(entry_date, date) else pd.Timestamp(entry_date).date(),
                    "entry_price": round(position_avg_price, 4),
                    "exit_date": last_date if isinstance(last_date, date) else pd.Timestamp(last_date).date(),
                    "exit_price": round(sell_price, 4),
                    "quantity": position_qty,
                    "pnl": round(pnl, 4),
                    "pnl_pct": round(pnl_pct, 4),
                    "holding_days": holding,
                    "signal_metadata": {"confidence": 0, "reason": "forced_close"},
                }
            )

        return trades, equity_points

    # ── OHLCV Veri Çekme ──

    async def _get_ohlcv_dataframe(
        self, ticker: str, start_date: date, end_date: date
    ) -> pd.DataFrame:
        """Sembol için tarih aralığında OHLCV verisini DataFrame olarak döndür."""
        from datetime import datetime as dt

        rows = await self.ohlcv_repo.get_ohlcv(
            symbol=ticker,
            interval="1d",
            start=dt.combine(start_date, dt.min.time()),
            end=dt.combine(end_date, dt.max.time()),
            limit=2000,
        )
        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(rows)
        if not df.empty and "time" in df.columns:
            df = df.sort_values("time").reset_index(drop=True)
        return df

    # ── Performans Metrikleri ──

    def _calculate_metrics(
        self,
        trades: list[dict],
        equity_points: list[dict],
        initial_capital: float,
        start_date: date,
        end_date: date,
    ) -> dict:
        """Backtest performans metriklerini hesapla."""
        total_trades = len(trades)

        if total_trades == 0:
            return {
                "total_return": 0,
                "cagr": 0,
                "sharpe_ratio": 0,
                "sortino_ratio": 0,
                "max_drawdown": 0,
                "win_rate": 0,
                "profit_factor": 0,
                "total_trades": 0,
                "avg_trade_pnl": 0,
                "avg_holding_days": 0,
            }

        # Trade bazlı metrikler
        pnls = [t["pnl"] for t in trades]
        winning = [p for p in pnls if p > 0]
        losing = [p for p in pnls if p <= 0]

        total_pnl = sum(pnls)
        win_rate = len(winning) / total_trades if total_trades > 0 else 0
        gross_profit = sum(winning) if winning else 0
        gross_loss = abs(sum(losing)) if losing else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")
        if profit_factor == float("inf"):
            profit_factor = 99.99

        avg_trade_pnl = total_pnl / total_trades if total_trades > 0 else 0
        holding_days_list = [t.get("holding_days", 0) or 0 for t in trades]
        avg_holding_days = (
            sum(holding_days_list) / len(holding_days_list)
            if holding_days_list
            else 0
        )

        # Total return
        final_value = initial_capital + total_pnl
        total_return = ((final_value - initial_capital) / initial_capital) * 100

        # CAGR
        days = (end_date - start_date).days
        years = days / 365.25 if days > 0 else 1
        if final_value > 0 and initial_capital > 0:
            cagr = ((final_value / initial_capital) ** (1 / years) - 1) * 100
        else:
            cagr = -100.0

        # Equity curve'den günlük getiriler
        daily_returns = self._compute_daily_returns(equity_points, initial_capital)

        # Sharpe Ratio (yıllıklandırılmış, risk-free = 0)
        sharpe_ratio = self._sharpe_ratio(daily_returns)

        # Sortino Ratio
        sortino_ratio = self._sortino_ratio(daily_returns)

        # Max Drawdown
        max_drawdown = self._max_drawdown(equity_points, initial_capital)

        return {
            "total_return": round(total_return, 4),
            "cagr": round(cagr, 4),
            "sharpe_ratio": round(sharpe_ratio, 4),
            "sortino_ratio": round(sortino_ratio, 4),
            "max_drawdown": round(max_drawdown, 4),
            "win_rate": round(win_rate, 4),
            "profit_factor": round(min(profit_factor, 99.99), 4),
            "total_trades": total_trades,
            "avg_trade_pnl": round(avg_trade_pnl, 4),
            "avg_holding_days": round(avg_holding_days, 2),
        }

    def _compute_daily_returns(
        self, equity_points: list[dict], initial_capital: float
    ) -> list[float]:
        """Equity points'ten günlük getiri yüzdelerini hesapla."""
        if not equity_points:
            return []

        # Tarihe göre grupla (birden fazla sembol olabilir)
        daily_values: dict[str, float] = {}
        for ep in equity_points:
            d = ep["date"]
            daily_values[d] = daily_values.get(d, 0) + ep["value"]

        sorted_dates = sorted(daily_values.keys())
        values = [daily_values[d] for d in sorted_dates]

        if len(values) < 2:
            return []

        returns = []
        prev = values[0] if values[0] > 0 else initial_capital
        for v in values[1:]:
            r = (v - prev) / prev if prev > 0 else 0
            returns.append(r)
            prev = v

        return returns

    def _sharpe_ratio(self, daily_returns: list[float]) -> float:
        """Yıllıklandırılmış Sharpe Ratio."""
        if len(daily_returns) < 2:
            return 0.0
        arr = np.array(daily_returns)
        mean_ret = np.mean(arr)
        std_ret = np.std(arr, ddof=1)
        if std_ret == 0:
            return 0.0
        return float(mean_ret / std_ret * math.sqrt(252))

    def _sortino_ratio(self, daily_returns: list[float]) -> float:
        """Yıllıklandırılmış Sortino Ratio."""
        if len(daily_returns) < 2:
            return 0.0
        arr = np.array(daily_returns)
        mean_ret = np.mean(arr)
        downside = arr[arr < 0]
        if len(downside) == 0:
            return 99.99  # Negatif getiri yok
        downside_std = np.std(downside, ddof=1)
        if downside_std == 0:
            return 0.0
        return float(mean_ret / downside_std * math.sqrt(252))

    def _max_drawdown(
        self, equity_points: list[dict], initial_capital: float
    ) -> float:
        """Maksimum drawdown yüzdesi (negatif değer)."""
        if not equity_points:
            return 0.0

        # Tarihe göre toplam değer
        daily_values: dict[str, float] = {}
        for ep in equity_points:
            d = ep["date"]
            daily_values[d] = daily_values.get(d, 0) + ep["value"]

        sorted_dates = sorted(daily_values.keys())
        values = [daily_values[d] for d in sorted_dates]

        if not values:
            return 0.0

        peak = values[0]
        max_dd = 0.0
        for v in values:
            if v > peak:
                peak = v
            dd = (v - peak) / peak if peak > 0 else 0
            if dd < max_dd:
                max_dd = dd

        return round(max_dd * 100, 4)  # Yüzde olarak (negatif)

    def _build_equity_curve(
        self, equity_points: list[dict], initial_capital: float
    ) -> dict:
        """Equity curve JSON yapısı oluştur."""
        if not equity_points:
            return {"dates": [], "values": [], "benchmark": []}

        # Tarihe göre toplam
        daily_values: dict[str, float] = {}
        for ep in equity_points:
            d = ep["date"]
            daily_values[d] = daily_values.get(d, 0) + ep["value"]

        sorted_dates = sorted(daily_values.keys())
        values = [daily_values[d] for d in sorted_dates]

        # Buy & Hold benchmark (ilk ve son değer arası lineer)
        benchmark = []
        if len(values) >= 2:
            start_val = initial_capital
            # Basit buy&hold: ilk gün al, son gün sat
            first_val = values[0] if values[0] > 0 else initial_capital
            ratio = initial_capital / first_val if first_val > 0 else 1
            benchmark = [round(v * ratio, 2) for v in values]
        else:
            benchmark = values[:]

        return {
            "dates": sorted_dates,
            "values": [round(v, 2) for v in values],
            "benchmark": benchmark,
        }

    # ── Sorgulama ──

    async def list_backtests(
        self,
        user_id: UUID,
        status: str | None = None,
        strategy_id: UUID | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[BacktestResultResponse], int]:
        """Kullanıcının backtest'lerini listele."""
        backtests = await self.backtest_repo.get_by_user(
            user_id=user_id,
            status=status,
            strategy_id=strategy_id,
            skip=skip,
            limit=limit,
        )
        total = await self.backtest_repo.count_by_user(
            user_id=user_id,
            status=status,
            strategy_id=strategy_id,
        )
        return [BacktestResultResponse.model_validate(b) for b in backtests], total

    async def get_backtest(self, backtest_id: UUID) -> BacktestResultResponse | None:
        """Backtest sonucunu getir."""
        backtest = await self.backtest_repo.get_by_id(backtest_id)
        if not backtest:
            return None
        return BacktestResultResponse.model_validate(backtest)

    async def get_backtest_detail(
        self, backtest_id: UUID
    ) -> BacktestDetailResponse | None:
        """Backtest detayını trade'lerle birlikte getir."""
        backtest = await self.backtest_repo.get_with_trades(backtest_id)
        if not backtest:
            return None
        return BacktestDetailResponse(
            **BacktestResultResponse.model_validate(backtest).model_dump(),
            trades=[BacktestTradeResponse.model_validate(t) for t in backtest.trades],
        )

    async def get_backtest_trades(
        self,
        backtest_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[BacktestTradeResponse], int]:
        """Backtest trade'lerini listele."""
        trades = await self.trade_repo.get_by_backtest(
            backtest_id=backtest_id, skip=skip, limit=limit
        )
        total = await self.trade_repo.count_by_backtest(backtest_id)
        return [BacktestTradeResponse.model_validate(t) for t in trades], total

    async def get_equity_curve(self, backtest_id: UUID) -> dict | None:
        """Backtest equity curve verisini getir."""
        backtest = await self.backtest_repo.get_by_id(backtest_id)
        if not backtest:
            return None
        return backtest.equity_curve

    async def delete_backtest(self, backtest_id: UUID, user_id: UUID) -> bool:
        """Backtest'i sil (sadece sahibi silebilir)."""
        backtest = await self.backtest_repo.get_by_id(backtest_id)
        if not backtest:
            return False
        if backtest.user_id != user_id:
            raise ValueError("Bu backtest size ait değil")
        await self.backtest_repo.delete(backtest)
        await self.db.commit()
        return True
