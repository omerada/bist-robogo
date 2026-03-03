"""BIST sembol ve endeks verilerini veritabanına yükler.

Kullanım: python -m scripts.seed_symbols
"""

import asyncio

from app.database import async_session_factory
from app.models.market import BistIndex, Symbol

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


async def seed():
    async with async_session_factory() as db:
        # Semboller
        for sym_data in BIST_30_SYMBOLS:
            symbol = Symbol(**sym_data, is_active=True)
            db.add(symbol)

        # Endeksler
        for idx_data in INDICES:
            index = BistIndex(**idx_data, is_active=True)
            db.add(index)

        await db.commit()
        print(f"✅ {len(BIST_30_SYMBOLS)} sembol ve {len(INDICES)} endeks yüklendi.")


if __name__ == "__main__":
    asyncio.run(seed())
