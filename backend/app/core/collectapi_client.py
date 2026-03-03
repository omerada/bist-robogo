"""CollectAPI piyasa veri sağlayıcı client.

BIST hisse senedi verileri için CollectAPI kullanılır.
API Dokümantasyon: https://collectapi.com/tr/api/economy

Kullanım:
    client = CollectAPIClient()
    data = await client.get_stock_prices()
"""

from decimal import Decimal
from typing import Any

import httpx
import structlog

from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class CollectAPIClient:
    """CollectAPI BIST veri entegrasyon client'ı."""

    BASE_URL = "https://api.collectapi.com/economy"
    TIMEOUT = 30

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or getattr(settings, "COLLECTAPI_KEY", "")
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"apikey {self.api_key}",
                },
                timeout=self.TIMEOUT,
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    # ── BIST Hisse Verileri ──

    async def get_all_stocks(self) -> list[dict[str, Any]]:
        """Tüm BIST hisse fiyatlarını çeker.

        Returns:
            [{"code": "THYAO", "text": "Türk Hava Yolları", "lastprice": "287.50",
              "rate": "2.14", "hacim": "5.234.567.890", "min": "280.00", "max": "290.00", ...}]
        """
        try:
            client = await self._get_client()
            response = await client.get("/allCurrency")
            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                return data.get("result", [])
            else:
                logger.warning("collectapi_all_stocks_failed", response=data)
                return []
        except httpx.HTTPError as exc:
            logger.error("collectapi_http_error", endpoint="allCurrency", error=str(exc))
            return []

    async def get_stock_price(self, symbol: str) -> dict[str, Any] | None:
        """Belirli bir hissenin fiyat bilgisini çeker.

        Args:
            symbol: BIST hisse kodu (örn: "THYAO")

        Returns:
            {"code": "THYAO", "lastprice": "287.50", "rate": "2.14", ...} veya None
        """
        stocks = await self.get_all_stocks()
        for stock in stocks:
            if stock.get("code", "").upper() == symbol.upper():
                return stock
        return None

    async def get_stock_prices(self, symbols: list[str]) -> dict[str, dict]:
        """Birden fazla hissenin fiyat bilgisini çeker.

        Args:
            symbols: BIST hisse kodları listesi

        Returns:
            {"THYAO": {...}, "GARAN": {...}, ...}
        """
        stocks = await self.get_all_stocks()
        symbol_set = {s.upper() for s in symbols}
        result = {}
        for stock in stocks:
            code = stock.get("code", "").upper()
            if code in symbol_set:
                result[code] = stock
        return result

    # ── BIST Endeks Verileri ──

    async def get_indices(self) -> list[dict[str, Any]]:
        """BIST endeks verilerini çeker (XU100, XU030 vb).

        Returns:
            [{"name": "BIST 100", "code": "XU100", "lastprice": "9234.56", ...}]
        """
        try:
            client = await self._get_client()
            response = await client.get("/indices")
            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                return data.get("result", [])
            else:
                logger.warning("collectapi_indices_failed", response=data)
                return []
        except httpx.HTTPError as exc:
            logger.error("collectapi_http_error", endpoint="indices", error=str(exc))
            return []

    # ── Döviz Kurları ──

    async def get_exchange_rates(self) -> list[dict[str, Any]]:
        """Döviz kurlarını çeker (USD/TRY, EUR/TRY vb).

        Returns:
            [{"name": "ABD DOLARI", "buying": "36.25", "selling": "36.38", ...}]
        """
        try:
            client = await self._get_client()
            response = await client.get("/exchange")
            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                return data.get("result", [])
            else:
                return []
        except httpx.HTTPError as exc:
            logger.error("collectapi_http_error", endpoint="exchange", error=str(exc))
            return []

    # ── Helper: Yapılandırılmış fiyat verisi ──

    @staticmethod
    def parse_stock_to_quote(stock_data: dict) -> dict:
        """CollectAPI ham hisse verisini standart fiyat formatına çevirir."""
        import decimal as _decimal

        try:
            last = stock_data.get("lastprice", "0")
            price = Decimal(str(last).replace(".", "").replace(",", ".")) if "," in str(last) else Decimal(str(last))
            min_val = stock_data.get("min", last)
            max_val = stock_data.get("max", last)
            min_price = Decimal(str(min_val).replace(".", "").replace(",", ".")) if "," in str(min_val) else Decimal(str(min_val))
            max_price = Decimal(str(max_val).replace(".", "").replace(",", ".")) if "," in str(max_val) else Decimal(str(max_val))

            volume_raw = stock_data.get("hacim", "0")
            volume = int(str(volume_raw).replace(".", "").replace(",", ""))
        except (ValueError, TypeError, _decimal.InvalidOperation):
            price = Decimal("0")
            min_price = Decimal("0")
            max_price = Decimal("0")
            volume = 0

        return {
            "symbol": stock_data.get("code", ""),
            "name": stock_data.get("text", ""),
            "price": float(price),
            "change_pct": stock_data.get("rate", "0"),
            "low": float(min_price),
            "high": float(max_price),
            "volume": volume,
        }
