# bist-robogo — Sistem Mimarisi Dokümanı

> **Proje:** bist-robogo — BIST İçin AI Destekli Otomatik Ticaret Platformu  
> **Versiyon:** 1.0  
> **Tarih:** 2026-03-03

---

## 1. Mimari Genel Bakış

bist-robogo, **mikro-servis yaklaşımlı modüler monolith** (modular monolith) mimarisi üzerine inşa edilmiştir. Bu yaklaşım, MVP aşamasında geliştirme hızı ve operasyonel basitlik sağlarken, sistem büyüdükçe bağımsız mikro-servislere ayrılmaya olanak tanır.

### 1.1 Mimari Diyagram (Üst Düzey)

```
                            ┌─────────────────────────────────────────────┐
                            │              FRONTEND (Next.js)              │
                            │  ┌─────────┐ ┌──────────┐ ┌─────────────┐  │
                            │  │Dashboard│ │Trend     │ │Strateji    │  │
                            │  │Ekranı   │ │Analiz    │ │Yönetimi    │  │
                            │  └────┬────┘ └────┬─────┘ └──────┬──────┘  │
                            └───────┼───────────┼──────────────┼──────────┘
                                    │           │              │
                              ┌─────▼───────────▼──────────────▼─────┐
                              │         API Gateway (Nginx/Traefik)   │
                              │    Rate Limiting · Auth · SSL · CORS  │
                              └─────────────────┬────────────────────┘
                                                │
                 ┌──────────────────────────────┼──────────────────────────────┐
                 │                    BACKEND (FastAPI)                         │
                 │                                                             │
                 │  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌───────────┐ │
                 │  │ Auth     │  │ Market   │  │ Trading   │  │ Strategy  │ │
                 │  │ Service  │  │ Data     │  │ Engine    │  │ Engine    │ │
                 │  │          │  │ Service  │  │           │  │           │ │
                 │  └──────────┘  └────┬─────┘  └─────┬─────┘  └─────┬─────┘ │
                 │                     │              │              │        │
                 │  ┌──────────┐  ┌────▼─────┐  ┌─────▼─────┐  ┌───▼──────┐ │
                 │  │ Risk     │  │ Data     │  │ Order     │  │ Backtest │ │
                 │  │ Manager  │  │ Pipeline │  │ Manager   │  │ Engine   │ │
                 │  │          │  │          │  │           │  │          │ │
                 │  └──────────┘  └──────────┘  └───────────┘  └──────────┘ │
                 │                                                             │
                 │  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌───────────┐ │
                 │  │ AI/ML    │  │ Notif.   │  │ Portfolio │  │ Scheduler │ │
                 │  │ Service  │  │ Service  │  │ Service   │  │ Service   │ │
                 │  └──────────┘  └──────────┘  └───────────┘  └───────────┘ │
                 └──────────────────────────────────────────────────────────────┘
                           │              │                │
              ┌────────────┼──────────────┼────────────────┼──────────┐
              │            │              │                │          │
        ┌─────▼────┐ ┌────▼─────┐ ┌──────▼──────┐ ┌──────▼───┐ ┌───▼────┐
        │PostgreSQL│ │Timescale │ │   Redis     │ │  Kafka/  │ │ MinIO  │
        │  (Ana)   │ │   DB     │ │  Cache+PubS │ │ Redpanda │ │  S3    │
        └──────────┘ └──────────┘ └─────────────┘ └──────────┘ └────────┘
```

### 1.2 Katmanlı Mimari

```
┌─────────────────────────────────────────────────────────┐
│                   Presentation Layer                     │
│          Next.js · React · TradingView Charts            │
├─────────────────────────────────────────────────────────┤
│                    API Gateway Layer                      │
│         Nginx/Traefik · Auth · Rate Limit · SSL          │
├─────────────────────────────────────────────────────────┤
│                   Application Layer                       │
│        FastAPI Routers · Business Logic · Services        │
├─────────────────────────────────────────────────────────┤
│                     Domain Layer                          │
│     Entities · Value Objects · Domain Services            │
├─────────────────────────────────────────────────────────┤
│                 Infrastructure Layer                      │
│  Repositories · Broker Adapters · ML Models · Messaging  │
├─────────────────────────────────────────────────────────┤
│                     Data Layer                            │
│   PostgreSQL · TimescaleDB · Redis · Kafka · MinIO       │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Modül Detayları

### 2.1 Auth Service (Kimlik Doğrulama ve Yetkilendirme)

**Sorumluluk:** Kullanıcı kaydı, giriş, JWT yönetimi, rol tabanlı erişim kontrolü.

| Özellik | Detay                                            |
| ------- | ------------------------------------------------ |
| Kayıt   | Email + şifre, email doğrulama                   |
| Giriş   | JWT (access + refresh token)                     |
| 2FA     | TOTP (Google Authenticator)                      |
| Roller  | admin, trader, viewer, api_user                  |
| Session | Redis tabanlı, httpOnly cookie                   |
| Audit   | Tüm giriş/çıkış ve yetki değişiklikleri loglanır |

**API Endpoints:**

```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout
POST   /api/v1/auth/2fa/enable
POST   /api/v1/auth/2fa/verify
GET    /api/v1/auth/me
```

---

### 2.2 Market Data Service (Piyasa Verisi Servisi)

**Sorumluluk:** Gerçek zamanlı ve geçmiş piyasa verilerinin toplanması, saklanması ve dağıtılması.

**Veri Akışı:**

```
┌──────────┐    ┌───────────────┐    ┌───────────┐    ┌───────────┐
│  Broker  │───▶│  Data Ingestion│───▶│   Kafka   │───▶│TimescaleDB│
│  APIs    │    │  Workers       │    │  Topics   │    │  Storage  │
└──────────┘    └───────────────┘    └─────┬─────┘    └───────────┘
                                           │
                                     ┌─────▼─────┐
                                     │  Redis    │
                                     │  Cache    │
                                     └─────┬─────┘
                                           │
                                     ┌─────▼─────┐
                                     │ WebSocket │
                                     │ Broadcast │
                                     └───────────┘
```

**Kafka Topics:**

```
market.ticks.{symbol}        # Gerçek zamanlı fiyat verisi
market.orderbook.{symbol}    # Order book güncellemeleri
market.trades.{symbol}       # Gerçekleşen işlemler
market.indices.updates       # Endeks güncellemeleri
market.corporate-actions     # Bedelsiz, temettü, bölünme vb.
```

**API Endpoints:**

```
GET    /api/v1/market/symbols                    # Sembol listesi
GET    /api/v1/market/symbols/{symbol}/quote     # Anlık fiyat
GET    /api/v1/market/symbols/{symbol}/history   # Geçmiş veri (OHLCV)
GET    /api/v1/market/symbols/{symbol}/orderbook # Order book
GET    /api/v1/market/indices                    # Endeks listesi
GET    /api/v1/market/indices/{index}/components # Endeks bileşenleri
WS     /ws/v1/market/stream                      # Canlı veri akışı
```

**Veri Normalizasyonu:**

- Tüm broker'lardan gelen veriler ortak format (OHLCV) standartına dönüştürülür.
- Corporate actions (split, dividend) otomatik olarak fiyatla düzeltilir.
- Veri kalite kontrolü: Boşluk tespiti, outlier tespiti, timestamp doğrulama.

---

### 2.3 Trading Engine (Ticaret Motoru)

**Sorumluluk:** Emir oluşturma, doğrulama, risk kontrolü, broker'a iletme ve durum takibi.

**Emir Yaşam Döngüsü:**

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Strateji │───▶│  Risk    │───▶│  Emir    │───▶│ Broker   │───▶│  Durum   │
│ Sinyali  │    │ Kontrol  │    │ Oluştur  │    │ Gönder   │    │ Takip    │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │               │               │               │
     │          Red ──┘          Hata ─┘         Fail ─┘         Event ─┘
     │               │               │               │               │
     │          ┌────▼────┐    ┌─────▼────┐    ┌─────▼────┐    ┌─────▼────┐
     │          │ Reject  │    │ Log &    │    │ Retry /  │    │ Update   │
     │          │ & Alert │    │ Alert    │    │ Alert    │    │ Position │
     │          └─────────┘    └──────────┘    └──────────┘    └──────────┘
```

**Emir Tipleri:**

- **Market Order:** Piyasa fiyatından anında alım/satım
- **Limit Order:** Belirli fiyattan alım/satım
- **Stop-Loss:** Kayıp sınırlama emri
- **Take-Profit:** Kar realizasyon emri
- **Trailing Stop:** Dinamik stop-loss
- **OCO (One-Cancels-Other):** Birini iptal eden ikili emir

**API Endpoints:**

```
POST   /api/v1/orders                     # Yeni emir oluştur
GET    /api/v1/orders                     # Emir listesi
GET    /api/v1/orders/{orderId}           # Emir detayı
PUT    /api/v1/orders/{orderId}           # Emir güncelle
DELETE /api/v1/orders/{orderId}           # Emir iptal
GET    /api/v1/orders/{orderId}/history   # Emir geçmişi
```

---

### 2.4 Risk Manager (Risk Yöneticisi)

**Sorumluluk:** Tüm emirlerin risk kurallarına uygunluğunu kontrol eder. Hiçbir emir risk kontrolünden geçmeden broker'a iletilmez.

**Risk Kontrol Kuralları:**

| Kural                     | Açıklama                                       | Varsayılan                   |
| ------------------------- | ---------------------------------------------- | ---------------------------- |
| Maks günlük zarar         | Gün içi toplam zarar limiti                    | Portföyün %2'si              |
| Maks pozisyon büyüklüğü   | Tek sembolde maks pozisyon                     | Portföyün %10'u              |
| Maks açık pozisyon sayısı | Aynı anda maks pozisyon                        | 10                           |
| Stop-loss zorunluluğu     | Her emir stop-loss ile birlikte                | Aktif                        |
| Maks emir büyüklüğü       | Tek emirde maks tutar                          | 50.000 TL                    |
| Volatilite filtresi       | Yüksek volatilite dönemlerinde emir kısıtlama  | VIX > 30 ise yarı pozisyon   |
| Korelasyon kontrolü       | Aynı yönde yüksek korelasyonlu pozisyon limiti | Maks 3 korelasyonlu pozisyon |
| Günlük emir limiti        | Gün içi maks emir sayısı                       | 50                           |
| Seans kontrolü            | Seans dışında emir engelleme                   | Aktif                        |

**Risk Hesaplama Katmanları:**

```
┌─────────────────────────────────────────────────┐
│           Pre-Trade Risk Checks                  │
│  ┌─────────┐ ┌───────────┐ ┌─────────────────┐ │
│  │Position │ │ Daily P&L │ │ Volatility      │ │
│  │Sizing   │ │ Limit     │ │ Assessment      │ │
│  └─────────┘ └───────────┘ └─────────────────┘ │
├─────────────────────────────────────────────────┤
│           Real-Time Risk Monitoring              │
│  ┌─────────┐ ┌───────────┐ ┌─────────────────┐ │
│  │Portfolio│ │ Drawdown  │ │ Exposure        │ │
│  │VaR      │ │ Monitor   │ │ Monitor         │ │
│  └─────────┘ └───────────┘ └─────────────────┘ │
├─────────────────────────────────────────────────┤
│           Post-Trade Risk Analysis               │
│  ┌─────────┐ ┌───────────┐ ┌─────────────────┐ │
│  │Trade    │ │ Risk      │ │ Performance     │ │
│  │Report   │ │ Attribution│ │ Attribution     │ │
│  └─────────┘ └───────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────┘
```

**API Endpoints:**

```
GET    /api/v1/risk/status                    # Güncel risk durumu
GET    /api/v1/risk/limits                    # Risk limitleri
PUT    /api/v1/risk/limits                    # Risk limiti güncelle
GET    /api/v1/risk/exposure                  # Açık pozisyon riski
GET    /api/v1/risk/daily-pnl                 # Günlük PnL
POST   /api/v1/risk/validate-order            # Emir risk kontrolü
```

---

### 2.5 Strategy Engine (Strateji Motoru)

**Sorumluluk:** Stratejilerin tanımlanması, çalıştırılması ve sinyal üretimi.

**Yerleşik Stratejiler:**

| Strateji           | Tip              | Açıklama                                |
| ------------------ | ---------------- | --------------------------------------- |
| MA Crossover       | Trend takip      | Hareketli ortalama kesişimi (SMA/EMA)   |
| RSI Mean Reversion | Ortalamaya dönüş | RSI aşırı alım/satım bölgeleri          |
| MACD Signal        | Momentum         | MACD sinyal çizgisi kesişimi            |
| Bollinger Breakout | Volatilite       | Bant dışı hareketlerde pozisyon         |
| Volume Profile     | Hacim analiz     | Hacim profili ile destek/direnç tespiti |
| AI Trend Predictor | ML tabanlı       | XGBoost/LSTM ile trend tahmini          |
| Dip Hunter         | AI + Teknik      | Olasılık tabanlı dip tespit stratejisi  |
| Momentum Ranking   | Momentum         | Sektör/endeks bazlı momentum sıralaması |

**Strateji Arayüzü (Abstract Base):**

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

class SignalType(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

@dataclass
class Signal:
    symbol: str
    signal_type: SignalType
    confidence: float          # 0.0 - 1.0
    price: float
    stop_loss: float | None
    take_profit: float | None
    metadata: dict

class BaseStrategy(ABC):

    @abstractmethod
    def name(self) -> str:
        """Strateji adı."""
        pass

    @abstractmethod
    def analyze(self, market_data: MarketData) -> list[Signal]:
        """Piyasa verisi ile analiz yap ve sinyal üret."""
        pass

    @abstractmethod
    def required_indicators(self) -> list[str]:
        """Gerekli teknik gösterge listesi."""
        pass

    def validate_signal(self, signal: Signal) -> bool:
        """Sinyal doğrulama (opsiyonel override)."""
        return signal.confidence >= 0.6
```

**API Endpoints:**

```
GET    /api/v1/strategies                       # Strateji listesi
POST   /api/v1/strategies                       # Yeni strateji oluştur
GET    /api/v1/strategies/{id}                  # Strateji detayı
PUT    /api/v1/strategies/{id}                  # Strateji güncelle
POST   /api/v1/strategies/{id}/activate         # Strateji aktifleştir
POST   /api/v1/strategies/{id}/deactivate       # Strateji deaktifleştir
GET    /api/v1/strategies/{id}/signals          # Strateji sinyalleri
GET    /api/v1/strategies/{id}/performance      # Strateji performansı
```

---

### 2.6 AI Service — OpenRouter LLM Entegrasyonu

**Sorumluluk:** OpenRouter LLM API gateway üzerinden teknik analiz, sohbet ve sinyal üretimi.

> **Not:** Orijinal planda lokal ML modelleri (XGBoost/LightGBM/MLflow/ONNX) planlanmıştı.
> Pratik geliştirme hızı ve bakım kolaylığı için OpenRouter LLM API gateway tercih edilmiştir.
> Mevcut teknik indikatörler (indicators/) LLM'e prompt context olarak beslenir.

**AI Pipeline:**

```
┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐
│  OHLCV +  │───▶│ Teknik    │───▶│ OpenRouter│───▶│ Yapısal   │
│  Market   │    │ Gösterge  │    │ LLM API   │    │ JSON Yanıt│
│  Data     │    │ Hesaplama │    │ (Chat/JSON)│    │ Parse     │
└───────────┘    └───────────┘    └───────────┘    └───────────┘
      │                │               │               │
 ┌────▼────┐     ┌─────▼────┐   ┌─────▼────┐    ┌────▼─────┐
 │SymbolRepo│     │ RSI,MACD │   │ Gemini   │    │ Pydantic │
 │ OHLCVRepo│     │ ADX,BB   │   │ GPT-4o   │    │ Schema   │
 │ Pandas   │     │ OBV,S/R  │   │ Claude   │    │ Fallback │
 └─────────┘     └──────────┘   └──────────┘    └──────────┘
```

**Gösterge Context (LLM'e Beslenen):**

| Gösterge Grubu | Metrikler                            |
| -------------- | ------------------------------------ |
| Momentum       | RSI, MACD, Stochastic K/D            |
| Trend          | SMA(20/50), EMA(12), ADX, OBV trend  |
| Volatilite     | Bollinger Bands (upper/middle/lower) |
| Destek/Direnç  | Support level, Resistance level      |
| Hacim          | Volume ratio                         |

**Servis Özellikleri:**

1. **Sembol Analizi** — Teknik göstergeler + LLM → BUY/SELL/HOLD önerisi
2. **Sohbet Asistanı** — Bağlamsal finans soru-cevap (sembol context opsiyonel)
3. **Toplu Sinyal Üretimi** — BIST-30 sembollerinde AI taraması
4. **AI Strateji** — BaseStrategy implementasyonu, LLM tabanlı sinyal üretimi
5. **Fallback Mekanizması** — API hatalarında gösterge bazlı basit analiz

**Yapılandırma:**

| Parametre                  | Varsayılan                     |
| -------------------------- | ------------------------------ |
| `OPENROUTER_API_KEY`       | (env)                          |
| `OPENROUTER_BASE_URL`      | `https://openrouter.ai/api/v1` |
| `OPENROUTER_DEFAULT_MODEL` | `google/gemini-2.5-flash`      |
| `OPENROUTER_MAX_TOKENS`    | 4096                           |
| `OPENROUTER_TEMPERATURE`   | 0.3                            |
| `OPENROUTER_TIMEOUT`       | 60s                            |

**API Endpoints:**

```
POST   /api/v1/ai/analyze              # Sembol AI analizi
POST   /api/v1/ai/chat                 # AI sohbet asistanı
GET    /api/v1/ai/signals               # Toplu AI sinyalleri
GET    /api/v1/ai/models                # Kullanılabilir LLM modelleri
GET    /api/v1/ai/settings              # AI ayarları
PUT    /api/v1/ai/settings              # AI ayarları güncelle
```

---

### 2.7 Backtest Engine (Geriye Dönük Test Motoru)

**Sorumluluk:** Stratejilerin geçmiş veri üzerinde simülasyonu ve performans analizi.

**Backtest Akışı:**

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Strateji + │───▶│  Geçmiş    │───▶│  Simülasyon │───▶│  Sonuç     │
│  Parametreler│    │  Veri Yükle │    │  Çalıştır   │    │  Raporu    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                            │
                                      ┌─────▼─────┐
                                      │Slippage   │
                                      │Komisyon   │
                                      │Likidite   │
                                      │Simülasyonu│
                                      └───────────┘
```

**Performans Metrikleri:**

- **Toplam Getiri (Total Return)**
- **Yıllıklandırılmış Getiri (CAGR)**
- **Sharpe Ratio**
- **Sortino Ratio**
- **Calmar Ratio**
- **Maksimum Drawdown**
- **Win Rate**
- **Profit Factor**
- **Ortalama Kazanç/Kayıp Oranı**
- **Recovery Factor**
- **Trade Count**
- **Holding Period**

**API Endpoints:**

```
POST   /api/v1/backtest/run                       # Backtest çalıştır
GET    /api/v1/backtest/results                    # Sonuç listesi
GET    /api/v1/backtest/results/{id}               # Sonuç detayı
GET    /api/v1/backtest/results/{id}/trades        # İşlem listesi
GET    /api/v1/backtest/results/{id}/equity-curve  # Equity curve
POST   /api/v1/backtest/optimize                   # Parametre optimizasyonu
```

---

### 2.8 Portfolio Service (Portföy Servisi)

**Sorumluluk:** Açık pozisyonlar, geçmiş işlemler, portföy değeri ve PnL hesaplaması.

**API Endpoints:**

```
GET    /api/v1/portfolio/summary                  # Portföy özeti
GET    /api/v1/portfolio/positions                # Açık pozisyonlar
GET    /api/v1/portfolio/positions/{symbol}       # Pozisyon detayı
GET    /api/v1/portfolio/history                  # İşlem geçmişi
GET    /api/v1/portfolio/pnl                      # Kar/Zarar raporu
GET    /api/v1/portfolio/pnl/daily                # Günlük PnL
GET    /api/v1/portfolio/pnl/monthly              # Aylık PnL
GET    /api/v1/portfolio/allocation               # Varlık dağılımı
```

---

### 2.9 Notification Service (Bildirim Servisi)

**Sorumluluk:** Sistem olaylarının kullanıcılara iletilmesi.

**Bildirim Kanalları:**

- **In-App Notification:** WebSocket ile anlık
- **Email:** SMTP (SendGrid / AWS SES)
- **Push Notification:** Firebase Cloud Messaging
- **Telegram Bot:** Opsiyonel alternatif kanal
- **SMS:** Kritik alarmlar için (Netgsm / İleti Merkezi)

**Bildirim Tipleri:**

```
ORDER_FILLED          # Emir gerçekleşti
ORDER_REJECTED        # Emir reddedildi
STOP_LOSS_TRIGGERED   # Stop-loss tetiklendi
SIGNAL_GENERATED      # Yeni strateji sinyali
RISK_LIMIT_WARNING    # Risk limiti uyarısı
RISK_LIMIT_BREACH     # Risk limiti aşıldı
DAILY_REPORT          # Günlük özet rapor
SYSTEM_ALERT          # Sistem uyarısı
PRICE_ALERT           # Fiyat alarmı
```

---

### 2.10 Scheduler Service (Zamanlayıcı Servisi)

**Sorumluluk:** Zamanlanmış görevlerin yönetimi.

**Zamanlanmış Görevler:**

| Görev                     | Periyot               | Açıklama                             |
| ------------------------- | --------------------- | ------------------------------------ |
| Günlük veri güncelleme    | Her gün 18:30         | BIST kapanış sonrası EOD veri çekme  |
| Endeks bileşen güncelleme | Haftalık (Pazartesi)  | Endeks bileşen listesi güncelleme    |
| Model yeniden eğitim      | Haftalık (Pazar)      | ML modellerinin yeni veriyle eğitimi |
| Portföy snapshot          | Her gün 18:00         | Günlük portföy değeri kaydı          |
| Risk raporu               | Her gün 18:45         | Günlük risk özet raporu              |
| Veritabanı bakım          | Haftalık (Pazar gece) | Vacuum, reindex, temizlik            |
| Yedekleme                 | Günlük 02:00          | Tam veritabanı yedekleme             |
| Sağlık kontrolü           | Her 1 dk              | Tüm servislerin health check'i       |

---

## 3. Veri Akış Diyagramları

### 3.1 Gerçek Zamanlı Veri Akışı

```
┌─────────┐  tick  ┌──────────┐  publish  ┌───────┐  subscribe  ┌──────────┐
│ Broker  │──────▶│  Data    │─────────▶│ Kafka │───────────▶│ Strategy │
│ API/WS  │       │ Ingestion│          │       │            │ Engine   │
└─────────┘       └────┬─────┘          └───┬───┘            └────┬─────┘
                       │                    │                     │
                  ┌────▼─────┐         ┌────▼────┐          ┌────▼─────┐
                  │Timescale │         │  Redis  │          │ Trading  │
                  │DB (store)│         │ (cache) │          │ Engine   │
                  └──────────┘         └────┬────┘          └──────────┘
                                            │
                                       ┌────▼────┐
                                       │WebSocket│
                                       │(clients)│
                                       └─────────┘
```

### 3.2 Emir Akışı

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Strateji │────▶│  Risk    │────▶│  Order   │────▶│ Broker   │────▶│  Order   │
│ veya     │     │ Manager  │     │ Manager  │     │ Adapter  │     │  Status  │
│ Manuel   │     │ ✓ / ✗    │     │          │     │          │     │  Update  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘     └──────────┘
                      │                                                   │
                      │ RED                                               │
                      ▼                                                   ▼
                 ┌──────────┐                                      ┌──────────┐
                 │ Reject + │                                      │ Portfolio │
                 │ Notify   │                                      │ Update   │
                 └──────────┘                                      └──────────┘
```

### 3.3 Backtest Akışı

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Strateji │────▶│ Geçmiş   │────▶│ Strateji │────▶│ Sonuç    │────▶│ Rapor    │
│ Seçimi + │     │ Veri     │     │ Simülas. │     │ Hesapla  │     │ Üretimi  │
│ Params   │     │ Yükleme  │     │ Döngüsü  │     │          │     │          │
└──────────┘     └──────────┘     └──────────┘     └──────────┘     └──────────┘
                                        │
                                  ┌─────▼──────┐
                                  │Slippage +  │
                                  │Commission  │
                                  │Simulation  │
                                  └────────────┘
```

---

## 4. Veritabanı Mimarisi

### 4.1 PostgreSQL — Ana Veritabanı

```
┌─────────────────────────────────────────────────┐
│                  PostgreSQL 16                    │
│                                                   │
│  ┌─────────┐  ┌───────────┐  ┌────────────────┐ │
│  │ users   │  │ strategies│  │ orders         │ │
│  │ roles   │  │ signals   │  │ order_history  │ │
│  │ sessions│  │ params    │  │ trades         │ │
│  └─────────┘  └───────────┘  └────────────────┘ │
│                                                   │
│  ┌───────────────┐  ┌───────────┐  ┌──────────┐ │
│  │ risk_rules    │  │ portfolios│  │ notif.   │ │
│  │ risk_events   │  │ positions │  │ alerts   │ │
│  │ risk_snapshots│  │ pnl_daily │  │ prefs    │ │
│  └───────────────┘  └───────────┘  └──────────┘ │
│                                                   │
│  ┌──────────────────┐  ┌─────────────────────┐   │
│  │ backtest_runs    │  │ audit_logs          │   │
│  │ backtest_results │  │ system_events       │   │
│  │ backtest_trades  │  │ api_keys            │   │
│  └──────────────────┘  └─────────────────────┘   │
└─────────────────────────────────────────────────┘
```

### 4.2 TimescaleDB — Zaman Serisi Veritabanı

```
┌─────────────────────────────────────────────────┐
│               TimescaleDB (PostgreSQL ext.)       │
│                                                   │
│  ┌──────────────────────────────────────────┐    │
│  │ ohlcv_1m  (1 dakikalık mum verisi)       │    │
│  │ ├── time, symbol, open, high, low,       │    │
│  │ │   close, volume, vwap                  │    │
│  │ └── Hypertable, chunk_interval: 1 week   │    │
│  └──────────────────────────────────────────┘    │
│                                                   │
│  ┌──────────────────────────────────────────┐    │
│  │ ohlcv_1d  (günlük mum verisi)            │    │
│  │ ├── Continuous Aggregate from ohlcv_1m   │    │
│  │ └── Materialized, refresh: daily         │    │
│  └──────────────────────────────────────────┘    │
│                                                   │
│  ┌──────────────────────────────────────────┐    │
│  │ ticks  (tick bazlı veri)                  │    │
│  │ ├── time, symbol, price, volume, side    │    │
│  │ └── Hypertable, compression after 7 days │    │
│  └──────────────────────────────────────────┘    │
│                                                   │
│  ┌──────────────────────────────────────────┐    │
│  │ indicator_values (hesaplanmış göstergeler)│    │
│  │ ├── time, symbol, indicator, value       │    │
│  │ └── Hypertable, retention: 2 years       │    │
│  └──────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

### 4.3 Redis — Önbellek ve Anlık Veri

```
Prefix yapısı:
  market:quote:{symbol}         → Son fiyat bilgisi (JSON)
  market:orderbook:{symbol}     → Order book snapshot
  market:signal:{strategy_id}   → Son üretilen sinyal
  user:session:{session_id}     → Kullanıcı oturum bilgisi
  risk:daily_pnl:{user_id}     → Günlük PnL (anlık)
  risk:exposure:{user_id}      → Açık pozisyon riski
  cache:api:{endpoint_hash}    → API önbellek
  rate:limit:{user_id}         → Rate limit sayacı
  ws:channels:{channel}        → WebSocket kanal abone listesi
```

---

## 5. Deployment Mimarisi

### 5.1 Docker Compose (Geliştirme & MVP)

```yaml
# docker-compose.yml yapısı
services:
  # Frontend
  frontend: # Next.js (port 3000)

  # Backend
  api: # FastAPI (port 8000)
  celery-worker: # Celery worker
  celery-beat: # Celery scheduler

  # Data
  postgres: # PostgreSQL + TimescaleDB (port 5432)
  redis: # Redis (port 6379)
  kafka: # Kafka/Redpanda (port 9092)

  # Monitoring
  prometheus: # Prometheus (port 9090)
  grafana: # Grafana (port 3001)

  # Storage
  minio: # MinIO S3 (port 9000)
```

### 5.2 Prodüksiyon Mimarisi (Kubernetes)

```
┌─────────────────────────────────────────────────────┐
│                   Kubernetes Cluster                  │
│                                                       │
│  ┌──────────────────────────────────────────────┐    │
│  │              Ingress Controller               │    │
│  │         (Nginx / Traefik + Cert-Manager)      │    │
│  └──────────────────────────────────────────────┘    │
│                                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐ │
│  │   Frontend  │  │   API       │  │   Workers    │ │
│  │   (2 pods)  │  │  (3 pods)   │  │  (2-5 pods)  │ │
│  │   Next.js   │  │  FastAPI    │  │  Celery      │ │
│  └─────────────┘  └─────────────┘  └──────────────┘ │
│                                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐ │
│  │  PostgreSQL │  │   Redis     │  │   Kafka      │ │
│  │  (StatefulS)│  │  (Sentinel) │  │  (3 brokers) │ │
│  └─────────────┘  └─────────────┘  └──────────────┘ │
│                                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐ │
│  │ Prometheus  │  │   Grafana   │  │    Loki      │ │
│  │             │  │             │  │              │ │
│  └─────────────┘  └─────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────┘
```

---

## 6. Güvenlik Mimarisi

```
┌─────────────────────────────────────────────────────────┐
│                    Security Layers                        │
│                                                           │
│  Layer 1: Network                                        │
│  ├── WAF (Web Application Firewall)                      │
│  ├── DDoS Protection                                     │
│  └── Firewall Rules (sadece gerekli portlar açık)        │
│                                                           │
│  Layer 2: Transport                                      │
│  ├── TLS 1.3 (tüm dış iletişim)                         │
│  └── mTLS (servisler arası — Kubernetes)                 │
│                                                           │
│  Layer 3: Application                                    │
│  ├── JWT Authentication (access + refresh)               │
│  ├── RBAC Authorization                                  │
│  ├── Rate Limiting (per-user, per-endpoint)              │
│  ├── Input Validation (Pydantic + Zod)                   │
│  ├── CORS Policy                                         │
│  └── CSRF Protection                                     │
│                                                           │
│  Layer 4: Data                                           │
│  ├── AES-256 at rest                                     │
│  ├── Parametrized queries (SQL injection önleme)         │
│  ├── Vault / Secrets Manager                             │
│  └── Broker API key şifreleme                            │
│                                                           │
│  Layer 5: Monitoring & Audit                             │
│  ├── Audit Log (tüm kritik işlemler)                     │
│  ├── Anomaly Detection (olağandışı işlem tespiti)        │
│  ├── Security Alerting                                   │
│  └── Penetration Testing (periyodik)                     │
└─────────────────────────────────────────────────────────┘
```

---

## 7. Monitoring ve Observability

### 7.1 Metrik Katmanları

| Katman   | Araç                        | Metrikler                                 |
| -------- | --------------------------- | ----------------------------------------- |
| Altyapı  | Prometheus + Node Exporter  | CPU, RAM, disk, ağ                        |
| Uygulama | Prometheus + custom metrics | Request count/latency, error rate         |
| İş       | Custom dashboard            | Günlük PnL, emir sayısı, sinyal doğruluğu |
| Veri     | TimescaleDB metrics         | Veri gecikmesi, boşluk sayısı             |
| ML       | MLflow + custom             | Model accuracy, drift, inference time     |

### 7.2 Alarm Kuralları

| Alarm                 | Koşul                         | Kanal                |
| --------------------- | ----------------------------- | -------------------- |
| API gecikme yüksek    | p95 > 500ms (5 dk)            | Slack + Email        |
| Hata oranı yüksek     | Error rate > %5 (1 dk)        | Slack + PagerDuty    |
| Broker bağlantı koptu | Health check fail (3 ardışık) | SMS + Slack          |
| Günlük zarar limiti   | PnL < -%2                     | SMS + Email + In-App |
| Disk doluluk          | > %85                         | Email                |
| Model drift tespit    | Accuracy drop > %10           | Email                |

---

## 8. Sonuç

Bu mimari doküman, bist-robogo platformunun tüm teknik bileşenlerini, veri akışlarını, güvenlik katmanlarını ve deployment stratejisini kapsamlı şekilde tanımlamaktadır. Modüler yapı sayesinde her bileşen bağımsız olarak geliştirilebilir, test edilebilir ve dağıtılabilir.

---

_Bu doküman, bist-robogo projesinin Ar-Ge sürecinin bir parçasıdır ve düzenli olarak güncellenecektir._
