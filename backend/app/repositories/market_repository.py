# Source: Doc 07 §12.2 pattern — Market repository
"""Market veritabanı erişim katmanı."""

import logging
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)

from app.models.market import BistIndex, IndexComponent, Symbol
from app.repositories.base import BaseRepository


class SymbolRepository(BaseRepository[Symbol]):
    """Symbol CRUD + özel sorgular."""

    def __init__(self, db: AsyncSession):
        super().__init__(Symbol, db)

    async def get_by_ticker(self, ticker: str) -> Symbol | None:
        stmt = select(Symbol).where(Symbol.ticker == ticker.upper())
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_symbols(
        self, skip: int = 0, limit: int = 100
    ) -> list[Symbol]:
        stmt = (
            select(Symbol)
            .where(Symbol.is_active.is_(True))
            .order_by(Symbol.ticker)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_active_count(self) -> int:
        stmt = select(func.count()).select_from(Symbol).where(Symbol.is_active.is_(True))
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def search(self, query: str, limit: int = 20) -> list[Symbol]:
        """Ticker veya isim ile arama."""
        pattern = f"%{query.upper()}%"
        stmt = (
            select(Symbol)
            .where(
                Symbol.is_active.is_(True),
                (Symbol.ticker.ilike(pattern)) | (Symbol.name.ilike(pattern)),
            )
            .order_by(Symbol.ticker)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_sector(self, sector: str) -> list[Symbol]:
        stmt = (
            select(Symbol)
            .where(Symbol.is_active.is_(True), Symbol.sector == sector)
            .order_by(Symbol.ticker)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_sectors(self) -> list[str]:
        """Benzersiz sektör listesi."""
        stmt = (
            select(Symbol.sector)
            .where(Symbol.is_active.is_(True), Symbol.sector.isnot(None))
            .distinct()
            .order_by(Symbol.sector)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class IndexRepository(BaseRepository[BistIndex]):
    """BistIndex CRUD + bileşen sorguları."""

    def __init__(self, db: AsyncSession):
        super().__init__(BistIndex, db)

    async def get_by_code(self, code: str) -> BistIndex | None:
        stmt = select(BistIndex).where(BistIndex.code == code.upper())
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_indices(self) -> list[BistIndex]:
        stmt = (
            select(BistIndex)
            .where(BistIndex.is_active.is_(True))
            .order_by(BistIndex.code)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_index_symbols(self, index_code: str) -> list[Symbol]:
        """Bir endeksin aktif bileşen sembollerini döner."""
        stmt = (
            select(Symbol)
            .join(IndexComponent, IndexComponent.symbol_id == Symbol.id)
            .join(BistIndex, BistIndex.id == IndexComponent.index_id)
            .where(
                BistIndex.code == index_code.upper(),
                IndexComponent.removed_at.is_(None),
                Symbol.is_active.is_(True),
            )
            .order_by(Symbol.ticker)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class OHLCVRepository:
    """OHLCV zaman serisi sorguları (TimescaleDB / raw SQL)."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_ohlcv(
        self,
        symbol: str,
        interval: str = "1d",
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int = 250,
    ) -> list[dict]:
        """OHLCV verisi döner.

        interval: 1m, 5m, 15m, 1h, 1d, 1w, 1M
        TimescaleDB time_bucket kullanır.
        """
        table = self._get_table_for_interval(interval)
        bucket = self._get_bucket_for_interval(interval)

        query_parts = [
            f"SELECT time_bucket(:bucket, time) AS time,",
            "  first(open, time) AS open,",
            "  max(high) AS high,",
            "  min(low) AS low,",
            "  last(close, time) AS close,",
            "  sum(volume) AS volume",
            f"FROM {table}",
            "WHERE symbol = :symbol",
        ]
        params: dict = {"symbol": symbol.upper(), "bucket": bucket}

        if start:
            query_parts.append("AND time >= :start")
            params["start"] = start
        if end:
            query_parts.append("AND time <= :end")
            params["end"] = end

        query_parts.append(f"GROUP BY 1 ORDER BY 1 DESC LIMIT :limit")
        params["limit"] = limit

        sql = text(" ".join(query_parts))
        try:
            result = await self.db.execute(sql, params)
            rows = result.fetchall()
        except Exception as exc:
            logger.warning("OHLCV sorgusu başarısız (tablo mevcut olmayabilir): %s", exc)
            await self.db.rollback()
            return []

        return [
            {
                "time": row.time.isoformat(),
                "open": float(row.open) if row.open else 0,
                "high": float(row.high) if row.high else 0,
                "low": float(row.low) if row.low else 0,
                "close": float(row.close) if row.close else 0,
                "volume": int(row.volume) if row.volume else 0,
            }
            for row in reversed(rows)  # Kronolojik sıra
        ]

    async def get_latest_price(self, symbol: str) -> dict | None:
        """En son fiyat bilgisini döner."""
        sql = text("""
            SELECT time, open, high, low, close, volume
            FROM ohlcv_1d
            WHERE symbol = :symbol
            ORDER BY time DESC
            LIMIT 2
        """)
        try:
            result = await self.db.execute(sql, {"symbol": symbol.upper()})
            rows = result.fetchall()
        except Exception as exc:
            logger.warning("get_latest_price başarısız (tablo mevcut olmayabilir): %s", exc)
            await self.db.rollback()
            return None

        if not rows:
            return None

        current = rows[0]
        prev_close = rows[1].close if len(rows) > 1 else current.open
        change = float(current.close) - float(prev_close)
        change_pct = (change / float(prev_close) * 100) if prev_close else 0

        return {
            "price": float(current.close),
            "open": float(current.open),
            "high": float(current.high),
            "low": float(current.low),
            "close_prev": float(prev_close),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "volume": int(current.volume),
            "updated_at": current.time.isoformat(),
        }

    async def has_data(self, symbol: str) -> bool:
        """Sembol için veri var mı kontrol eder."""
        sql = text("SELECT EXISTS(SELECT 1 FROM ohlcv_1d WHERE symbol = :symbol LIMIT 1)")
        try:
            result = await self.db.execute(sql, {"symbol": symbol.upper()})
            return result.scalar_one()
        except Exception:
            await self.db.rollback()
            return False

    def _get_table_for_interval(self, interval: str) -> str:
        """Interval'a göre tablo adı döner."""
        if interval in ("1m", "5m", "15m"):
            return "ohlcv_1m"
        return "ohlcv_1d"

    def _get_bucket_for_interval(self, interval: str) -> str:
        """TimescaleDB time_bucket interval stringi."""
        mapping = {
            "1m": "1 minute",
            "5m": "5 minutes",
            "15m": "15 minutes",
            "1h": "1 hour",
            "1d": "1 day",
            "1w": "1 week",
            "1M": "1 month",
        }
        return mapping.get(interval, "1 day")
