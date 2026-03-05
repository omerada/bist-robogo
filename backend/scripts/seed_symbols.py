"""BIST sembol ve endeks verilerini veritabanına yükler.

Kullanım: python -m scripts.seed_symbols

CollectAPI key varsa tüm BIST sembollerini dinamik olarak çeker.
Key yoksa veya API erişimi başarısız olursa statik BIST 30 listesini kullanır.
"""

import asyncio
from datetime import date

from sqlalchemy import select

from app.database import async_session_factory
from app.models.market import BistIndex, IndexComponent, Symbol

# BIST 30 Sembolleri (Mart 2026 tahmini — gerçek listeye göre güncellenmeli)
BIST_30_SYMBOLS = [
    {"ticker": "AKBNK", "name": "Akbank", "sector": "Bankacılık"},
    {"ticker": "ARCLK", "name": "Arçelik", "sector": "Dayanıklı Tüketim"},
    {"ticker": "ASELS", "name": "Aselsan", "sector": "Savunma"},
    {"ticker": "BIMAS", "name": "BİM Mağazalar", "sector": "Perakende"},
    {"ticker": "EKGYO", "name": "Emlak Konut GYO", "sector": "GYO"},
    {"ticker": "EREGL", "name": "Ereğli Demir Çelik", "sector": "Metal"},
    {"ticker": "FROTO", "name": "Ford Otosan", "sector": "Otomotiv"},
    {"ticker": "GARAN", "name": "Garanti BBVA", "sector": "Bankacılık"},
    {"ticker": "GUBRF", "name": "Gübre Fabrikaları", "sector": "Kimya"},
    {"ticker": "HEKTS", "name": "Hektaş", "sector": "Kimya"},
    {"ticker": "ISCTR", "name": "İş Bankası C", "sector": "Bankacılık"},
    {"ticker": "KCHOL", "name": "Koç Holding", "sector": "Holding"},
    {"ticker": "KOZAL", "name": "Koza Altın", "sector": "Madencilik"},
    {"ticker": "KOZAA", "name": "Koza Anadolu Metal", "sector": "Madencilik"},
    {"ticker": "KRDMD", "name": "Kardemir D", "sector": "Metal"},
    {"ticker": "MGROS", "name": "Migros", "sector": "Perakende"},
    {"ticker": "ODAS", "name": "Odaş Elektrik", "sector": "Enerji"},
    {"ticker": "OYAKC", "name": "Oyak Çimento", "sector": "Çimento"},
    {"ticker": "PETKM", "name": "Petkim", "sector": "Petrokimya"},
    {"ticker": "PGSUS", "name": "Pegasus", "sector": "Havacılık"},
    {"ticker": "SAHOL", "name": "Sabancı Holding", "sector": "Holding"},
    {"ticker": "SASA", "name": "SASA Polyester", "sector": "Kimya"},
    {"ticker": "SISE", "name": "Şişecam", "sector": "Cam"},
    {"ticker": "TAVHL", "name": "TAV Havalimanları", "sector": "Havacılık"},
    {"ticker": "TCELL", "name": "Turkcell", "sector": "Telekomünikasyon"},
    {"ticker": "THYAO", "name": "Türk Hava Yolları", "sector": "Havacılık"},
    {"ticker": "TKFEN", "name": "Tekfen Holding", "sector": "Holding"},
    {"ticker": "TOASO", "name": "Tofaş", "sector": "Otomotiv"},
    {"ticker": "TUPRS", "name": "Tüpraş", "sector": "Enerji"},
    {"ticker": "YKBNK", "name": "Yapı Kredi Bankası", "sector": "Bankacılık"},
]

# Endeksler
INDICES = [
    {"code": "XU030", "name": "BIST 30", "description": "BIST en büyük 30 şirket"},
    {"code": "XU100", "name": "BIST 100", "description": "BIST en büyük 100 şirket"},
    {"code": "XKTUM", "name": "Katılım Tüm", "description": "Katılım Endeksi Tüm"},
    {"code": "XUSIN", "name": "BIST Sınai", "description": "BIST Sınai Endeksi"},
    {"code": "XBANK", "name": "BIST Banka", "description": "BIST Banka Endeksi"},
]

# Endeks → sembol eşlemeleri
INDEX_COMPONENTS = {
    "XU030": [s["ticker"] for s in BIST_30_SYMBOLS],  # tüm 30 sembol
    "XU100": [s["ticker"] for s in BIST_30_SYMBOLS],  # BIST30 XU100'ün alt kümesi
    "XBANK": ["AKBNK", "GARAN", "ISCTR", "YKBNK"],
    "XUSIN": ["ARCLK", "ASELS", "EREGL", "FROTO", "KRDMD", "PETKM", "SASA", "SISE", "TOASO"],
    "XKTUM": [
        "AKBNK", "ASELS", "BIMAS", "EREGL", "FROTO", "GARAN", "KCHOL",
        "MGROS", "SAHOL", "TCELL", "THYAO", "TKFEN", "TUPRS",
    ],
}


async def seed():
    # CollectAPI'den dinamik olarak tüm sembolleri çekmeye çalış
    dynamic_symbols = await _fetch_dynamic_symbols()
    all_symbols = dynamic_symbols if dynamic_symbols else BIST_30_SYMBOLS

    async with async_session_factory() as db:
        # Semboller — zaten var mı kontrol et
        existing = await db.execute(select(Symbol.ticker))
        existing_tickers = set(existing.scalars().all())

        new_symbols = 0
        for sym_data in all_symbols:
            if sym_data["ticker"] not in existing_tickers:
                symbol = Symbol(**sym_data, is_active=True)
                db.add(symbol)
                new_symbols += 1

        # Endeksler — zaten var mı kontrol et
        existing_idx = await db.execute(select(BistIndex.code))
        existing_codes = set(existing_idx.scalars().all())

        new_indices = 0
        for idx_data in INDICES:
            if idx_data["code"] not in existing_codes:
                index = BistIndex(**idx_data, is_active=True)
                db.add(index)
                new_indices += 1

        await db.flush()

        # Endeks bileşenleri — sembol ↔ endeks ilişkileri
        # Tüm sembol ve endeks ID'lerini çek
        symbols_result = await db.execute(select(Symbol))
        symbols_by_ticker = {s.ticker: s for s in symbols_result.scalars().all()}

        indices_result = await db.execute(select(BistIndex))
        indices_by_code = {i.code: i for i in indices_result.scalars().all()}

        # Mevcut bileşenleri kontrol et
        existing_comp = await db.execute(select(IndexComponent.index_id, IndexComponent.symbol_id))
        existing_pairs = set((str(r[0]), str(r[1])) for r in existing_comp.fetchall())

        new_components = 0
        today = date.today()
        for index_code, tickers in INDEX_COMPONENTS.items():
            if index_code not in indices_by_code:
                continue
            index = indices_by_code[index_code]
            for ticker in tickers:
                if ticker not in symbols_by_ticker:
                    continue
                symbol = symbols_by_ticker[ticker]
                pair = (str(index.id), str(symbol.id))
                if pair not in existing_pairs:
                    comp = IndexComponent(
                        index_id=index.id,
                        symbol_id=symbol.id,
                        weight=round(1.0 / len(tickers), 6),
                        added_at=today,
                    )
                    db.add(comp)
                    new_components += 1

        await db.commit()
        print(f"✅ Semboller: {new_symbols} yeni ({len(all_symbols)} toplam)")
        print(f"✅ Endeksler: {new_indices} yeni ({len(INDICES)} toplam)")
        print(f"✅ Endeks bileşenleri: {new_components} yeni ilişki oluşturuldu")


async def _fetch_dynamic_symbols() -> list[dict]:
    """CollectAPI'den tüm BIST sembollerini dinamik olarak çeker.

    API key yoksa veya hata olursa boş liste döner (statik listeye fallback yapılır).
    """
    try:
        from app.config import get_settings
        settings = get_settings()
        if not settings.COLLECTAPI_KEY:
            print("⚠️ COLLECTAPI_KEY tanımlı değil — statik BIST 30 listesi kullanılacak")
            return []

        from app.core.collectapi_client import CollectAPIClient
        client = CollectAPIClient()
        try:
            stocks = await client.get_all_stocks()
            if not stocks:
                print("⚠️ CollectAPI'den veri alınamadı — statik liste kullanılacak")
                return []

            symbols = []
            for stock in stocks:
                code = stock.get("code", "").upper().strip()
                name = stock.get("text", "").strip()
                if not code or not name:
                    continue
                symbols.append({
                    "ticker": code,
                    "name": name,
                    "sector": None,  # CollectAPI sektör bilgisi vermez
                })

            print(f"🔄 CollectAPI'den {len(symbols)} sembol çekildi")
            return symbols
        finally:
            await client.close()
    except Exception as exc:
        print(f"⚠️ Dinamik sembol çekme başarısız: {exc} — statik liste kullanılacak")
        return []


if __name__ == "__main__":
    asyncio.run(seed())
