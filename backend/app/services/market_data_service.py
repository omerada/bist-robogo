# Source: Doc 02 §2.2 — Market data service
"""Piyasa verisi iş mantığı katmanı."""

from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.market import BistIndex, Symbol
from app.repositories.market_repository import (
    IndexRepository,
    OHLCVRepository,
    SymbolRepository,
)
from app.schemas.market import OHLCVResponse, QuoteResponse, SymbolResponse


class MarketDataService:
    """Piyasa verisi iş mantığı — repository pattern üzerinden."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.symbol_repo = SymbolRepository(db)
        self.index_repo = IndexRepository(db)
        self.ohlcv_repo = OHLCVRepository(db)

    # ── Sembol İşlemleri ──

    async def get_symbols(
        self,
        index_code: str | None = None,
        sector: str | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[SymbolResponse], int]:
        """Sembol listesi + toplam sayı.

        Filtreleme: endeks kodu, sektör, arama.
        """
        if search:
            symbols = await self.symbol_repo.search(search, limit=limit)
            total = len(symbols)
        elif index_code:
            symbols = await self.index_repo.get_index_symbols(index_code)
            total = len(symbols)
            symbols = symbols[skip : skip + limit]
        elif sector:
            symbols = await self.symbol_repo.get_by_sector(sector)
            total = len(symbols)
            symbols = symbols[skip : skip + limit]
        else:
            symbols = await self.symbol_repo.get_active_symbols(skip=skip, limit=limit)
            total = await self.symbol_repo.get_active_count()

        return [SymbolResponse.model_validate(s) for s in symbols], total

    async def get_symbol_detail(self, ticker: str) -> SymbolResponse | None:
        """Tek sembol detayı."""
        symbol = await self.symbol_repo.get_by_ticker(ticker)
        if not symbol:
            return None
        return SymbolResponse.model_validate(symbol)

    # ── Endeks İşlemleri ──

    async def get_indices(self) -> list[dict]:
        """Aktif endeks listesi."""
        indices = await self.index_repo.get_active_indices()
        return [
            {
                "id": str(idx.id),
                "code": idx.code,
                "name": idx.name,
                "description": idx.description,
            }
            for idx in indices
        ]

    # ── Fiyat / Quote ──

    async def get_quote(self, ticker: str) -> QuoteResponse | None:
        """Anlık/son fiyat bilgisi.

        TimescaleDB'den son günlük OHLCV verisini çeker.
        Gerçek zamanlı veri geldiğinde WebSocket ile güncellenecek.
        """
        symbol = await self.symbol_repo.get_by_ticker(ticker)
        if not symbol:
            return None

        price_data = await self.ohlcv_repo.get_latest_price(ticker)
        if not price_data:
            # Veri yoksa minimal response
            return QuoteResponse(
                symbol=symbol.ticker,
                name=symbol.name,
                price=0,
                change=0,
                change_pct=0,
                open=0,
                high=0,
                low=0,
                close_prev=0,
                volume=0,
                bid=0,
                ask=0,
                updated_at=datetime.utcnow(),
            )

        return QuoteResponse(
            symbol=symbol.ticker,
            name=symbol.name,
            price=price_data["price"],
            change=price_data["change"],
            change_pct=price_data["change_pct"],
            open=price_data["open"],
            high=price_data["high"],
            low=price_data["low"],
            close_prev=price_data["close_prev"],
            volume=price_data["volume"],
            bid=price_data["price"] * 0.999,  # Placeholder — gerçek tick verisi gelince güncellenecek
            ask=price_data["price"] * 1.001,
            updated_at=datetime.fromisoformat(price_data["updated_at"]),
        )

    # ── OHLCV ──

    async def get_ohlcv(
        self,
        ticker: str,
        interval: str = "1d",
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int = 250,
    ) -> list[dict]:
        """OHLCV zaman serisi verisi."""
        # Sembol doğrulama
        symbol = await self.symbol_repo.get_by_ticker(ticker)
        if not symbol:
            return []

        return await self.ohlcv_repo.get_ohlcv(
            symbol=ticker,
            interval=interval,
            start=start,
            end=end,
            limit=limit,
        )

    # ── Sektörler ──

    async def get_sectors(self) -> list[str]:
        """Benzersiz sektör listesi."""
        return await self.symbol_repo.get_sectors()
