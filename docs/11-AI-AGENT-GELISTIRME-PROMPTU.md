# bist-robogo — AI Agent Geliştirme Promptu

> **Proje:** bist-robogo — BIST İçin AI Destekli Otomatik Ticaret Platformu  
> **Versiyon:** 1.0  
> **Tarih:** 2026-03-03  
> **Amaç:** Bu doküman, bir AI Agent'ın (Copilot, Cursor vb.) projeyi uçtan uca SIFIR HATA ile geliştirebilmesi için yazılmış master prompt ve yol haritasıdır.  
> **Kapsam:** Tüm backend, frontend, altyapı, test ve deployment adımları.

---

## ⚠️ KRİTİK KURALLAR — GELİŞTİRMEYE BAŞLAMADAN ÖNCE OKU

### Temel İlkeler

1. **ASLA tahmin yapma.** Her dosya için mutlaka ilgili dokümanı kontrol et. Dokümanlar tek kaynak (single source of truth).
2. **Dosya oluşturmadan ÖNCE** ilgili doküman bölümünü oku ve kodu oradan al.
3. **Her adım tamamlandığında doğrulama yap** — test çalıştır, lint kontrol et, build al.
4. **Hata alırsan durma** — hatayı analiz et, ilgili dokümana dön, düzelt.
5. **Sırayı takip et** — bağımlılıklar zincir halinde. Sıra atlamak bozulmaya yol açar.
6. **Her dosyada `# Source: Doc XX §Y` yorum satırı ekle** — referans izlenebilirliği için.
7. **Ortam değişkenlerini `.env.example` dosyasından al** — hardcode yapma.

### Bilinen Tutarsızlıklar ve Çözümleri

> Bu projede bazı dokümanlar arası tutarsızlıklar tespit edilmiştir. Aşağıda **kesin karar** verilmiş çözümler listelenmiştir. Bu kararlar dokümanlardaki bilgiyi override eder.

| #   | Tutarsızlık                                                                                                    | Kesin Karar                                                                                                                                                                |
| --- | -------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **Backend Dockerfile:** Doc 07 §22 (`virtualenvs.create false`) vs Doc 10 §2.1 (`virtualenvs.in-project true`) | ✅ **Doc 10 §2.1'i kullan.** `virtualenvs.in-project true` + multi-stage build. Doc 07 §22'yi yoksay.                                                                      |
| 2   | **DB credentials:** docker-compose'da `bist_user:bist_dev_pass_2026` vs config.py'de `bist:bist_secret`        | ✅ **docker-compose.yml değerlerini kullan.** config.py varsayılanlarını docker-compose ile uyumlu yap: `POSTGRES_USER=bist_user`, `POSTGRES_PASSWORD=bist_dev_pass_2026`. |
| 3   | **Redis parola:** docker-compose'da `bist_redis_pass_2026`, config.py'de parolasız                             | ✅ **Parolalı kullan.** `REDIS_URL=redis://:bist_redis_pass_2026@localhost:6379/0`                                                                                         |
| 4   | **Health check endpoint:** `/api/health` vs `/health`                                                          | ✅ **`/health` kullan.** Doc 07 §10.2'deki gibi root-level health router. Dockerfile HEALTHCHECK'i de `/health` olarak güncelle.                                           |
| 5   | **Celery broker config:** Hardcoded Redis URL türetme vs env var                                               | ✅ **Ayrı env var kullan.** `CELERY_BROKER_URL` ve `CELERY_RESULT_BACKEND` olarak docker-compose'dan oku. `celery_app.py`'deki hardcoded türetmeyi kaldır.                 |
| 6   | **socket.io-client:** bağımlılık olarak var ama kullanılmıyor                                                  | ✅ **Kaldır.** Frontend pnpm bağımlılığından `socket.io-client`'ı çıkar. WebSocket hook native `WebSocket` API kullanıyor.                                                 |
| 7   | **docker-compose dosya yolu:** Makefile `infra/docker/docker-compose.yml` referansı vs Doc 10 root-level       | ✅ **`docker-compose.yml`'yi proje kök dizinine koy.** Makefile'ı buna göre güncelle (`docker-compose up -d`).                                                             |
| 8   | **Doc 10 §7 referans haritası bölüm numaraları:** Kayma var                                                    | ✅ **Bu dokümandaki (Doc 11) referans haritasını kullan.** Doc 10 §7'yi yoksay, aşağıdaki haritayı takip et.                                                               |
| 9   | **FastAPI app import:** `app.main:app` vs `app.main:create_app`                                                | ✅ **`create_app()` factory kullan.** uvicorn'da `app.main:app` çağır — `app = create_app()` satırı main.py sonunda olmalı.                                                |

---

## 📐 PROJE MİMARİSİ ÖZETİ

### Teknoloji Stack (Kesin Sürümler)

| Katman                  | Teknoloji                                | Sürüm           |
| ----------------------- | ---------------------------------------- | --------------- |
| Backend Runtime         | Python                                   | 3.12+           |
| Backend Framework       | FastAPI                                  | 0.115+          |
| Backend ORM             | SQLAlchemy                               | 2.0+            |
| Backend Migration       | Alembic                                  | 1.13+           |
| Backend Validation      | Pydantic                                 | 2.0+            |
| Backend Task Queue      | Celery                                   | 5.4+            |
| Backend Paket Yönetimi  | Poetry                                   | 1.8+            |
| Frontend Framework      | Next.js                                  | 15+             |
| Frontend UI             | React                                    | 19+             |
| Frontend Language       | TypeScript                               | 5.x             |
| Frontend CSS            | TailwindCSS                              | 4+              |
| Frontend Component      | shadcn/ui                                | latest          |
| Frontend Chart          | lightweight-charts                       | 4+              |
| Frontend State          | Zustand                                  | 5+              |
| Frontend Data Fetching  | TanStack Query                           | 5+              |
| Frontend Paket Yönetimi | pnpm                                     | 9+              |
| Database                | PostgreSQL                               | 16              |
| TimeSeries              | TimescaleDB                              | 2.x (extension) |
| Cache                   | Redis                                    | 7+              |
| Message Queue           | Redpanda (Kafka uyumlu)                  | latest          |
| Object Storage          | MinIO                                    | latest          |
| Monitoring              | Prometheus + Grafana                     | latest          |
| Logging                 | structlog (backend), Loki (aggregation)  | latest          |
| Error Tracking          | Sentry                                   | latest          |
| ML Tracking             | MLflow                                   | latest          |
| ML Libraries            | scikit-learn, XGBoost, LightGBM, PyTorch | latest          |
| Technical Analysis      | TA-Lib, pandas-ta                        | latest          |
| Containerization        | Docker + Docker Compose                  | latest          |
| CI/CD                   | GitHub Actions                           | -               |

### Dizin Yapısı (Master — Kesin)

```
bist-robogo/
├── docs/                                    # Proje dokümanları (11 adet)
│   ├── 01-ARGE-GEREKSINIM-ANALIZI.md
│   ├── 02-SISTEM-MIMARISI.md
│   ├── 03-VERI-MODELLERI-VE-API.md
│   ├── 04-FRONTEND-TASARIM-VE-UX.md
│   ├── 05-GELISTIRME-PLANI-VE-MVP.md
│   ├── 06-EKSIK-ANALIZ-RAPORU.md
│   ├── 07-BACKEND-IMPLEMENTASYON-KILAVUZU.md
│   ├── 08-FRONTEND-IMPLEMENTASYON-KILAVUZU.md
│   ├── 09-TASARIM-SISTEMI.md
│   ├── 10-ADIM-ADIM-GELISTIRME-REHBERI.md
│   └── 11-AI-AGENT-GELISTIRME-PROMPTU.md
│
├── backend/                                 # Python Backend (FastAPI)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                          # FastAPI app factory ← Doc 07 §5
│   │   ├── config.py                        # Pydantic Settings ← Doc 07 §2
│   │   ├── database.py                      # SQLAlchemy engine/session ← Doc 07 §3
│   │   ├── dependencies.py                  # FastAPI DI ← Doc 07 §9
│   │   ├── exceptions.py                    # Custom exceptions ← Doc 07 §7
│   │   ├── middleware.py                     # Request logging, rate limit ← Doc 07 §6
│   │   ├── logging_config.py                # structlog setup ← Doc 07 §19
│   │   │
│   │   ├── api/                             # API Router'lar
│   │   │   ├── __init__.py
│   │   │   ├── router.py                    # Ana router ← Doc 07 §10
│   │   │   ├── health.py                    # Health check ← Doc 07 §10.2
│   │   │   └── v1/                          # Versiyonlu API
│   │   │       ├── __init__.py
│   │   │       ├── auth.py                  # Auth endpoints ← Doc 07 §10.3, Doc 02 §2.1
│   │   │       ├── market.py                # Market data endpoints ← Doc 03 §3.3
│   │   │       ├── orders.py                # Order endpoints ← Doc 03 §3.4
│   │   │       ├── portfolio.py             # Portfolio endpoints ← Doc 03 §3.5
│   │   │       ├── strategies.py            # Strategy endpoints ← Doc 02 §2.5
│   │   │       ├── backtest.py              # Backtest endpoints ← Doc 02 §2.7
│   │   │       ├── risk.py                  # Risk endpoints ← Doc 03 §3.7
│   │   │       ├── analysis.py              # Trend analysis endpoints ← Doc 03 §3.6
│   │   │       └── notifications.py         # Notification endpoints ← Doc 02 §2.9
│   │   │
│   │   ├── core/                            # Çekirdek modüller
│   │   │   ├── __init__.py
│   │   │   ├── security.py                  # JWT + bcrypt ← Doc 07 §8
│   │   │   ├── redis_client.py              # Redis manager ← Doc 07 §13
│   │   │   ├── rate_limiter.py              # Rate limiter ← Doc 07 §14
│   │   │   ├── websocket_manager.py         # WS channel mgr ← Doc 07 §15
│   │   │   └── kafka_client.py              # Kafka producer/consumer ← Doc 02 §2.2
│   │   │
│   │   ├── models/                          # SQLAlchemy ORM modelleri
│   │   │   ├── __init__.py                  # Re-export all ← Doc 07 §4.3
│   │   │   ├── base.py                      # Base, mixins ← Doc 07 §4.1
│   │   │   ├── user.py                      # User, ApiKey ← Doc 07 §4.2
│   │   │   ├── market.py                    # Symbol, Index ← Doc 03 §2 (symbols, indices)
│   │   │   ├── broker.py                    # BrokerConnection ← Doc 03 §2 (broker_connections)
│   │   │   ├── strategy.py                  # Strategy, Signal ← Doc 03 §2 (strategies, signals)
│   │   │   ├── order.py                     # Order, Trade ← Doc 03 §2 (orders, trades)
│   │   │   ├── portfolio.py                 # Position, Portfolio ← Doc 03 §2 (positions, portfolios)
│   │   │   ├── risk.py                      # RiskRule ← Doc 03 §2 (risk_rules)
│   │   │   ├── backtest.py                  # BacktestRun, BacktestTrade ← Doc 03 §2 (backtest_runs/trades)
│   │   │   ├── notification.py              # Notification ← Doc 03 §2 (notifications)
│   │   │   └── audit.py                     # AuditLog ← Doc 03 §2 (audit_logs)
│   │   │
│   │   ├── schemas/                         # Pydantic şemaları
│   │   │   ├── __init__.py
│   │   │   ├── common.py                    # APIResponse, PaginationMeta ← Doc 07 §11.1
│   │   │   ├── auth.py                      # Register, Login, Token ← Doc 07 §11.2
│   │   │   ├── market.py                    # Quote, OHLCV ← Doc 03 §4 (Pydantic modelleri)
│   │   │   ├── order.py                     # OrderCreate, OrderResponse ← Doc 03 §4
│   │   │   ├── portfolio.py                 # PortfolioSummary, Position ← Doc 03 §4
│   │   │   ├── strategy.py                  # StrategyCreate, Signal ← Doc 03 §4
│   │   │   ├── backtest.py                  # BacktestRequest, BacktestResult ← Doc 03 §4
│   │   │   ├── risk.py                      # RiskStatus ← Doc 03 §3.7
│   │   │   └── analysis.py                  # TrendAnalysis, Candidates ← Doc 03 §3.6
│   │   │
│   │   ├── services/                        # İş mantığı katmanı
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py              # ← Doc 02 §2.1 iş mantığı
│   │   │   ├── market_data_service.py       # ← Doc 02 §2.2 + broker veri çekme
│   │   │   ├── trading_service.py           # ← Doc 02 §2.3 emir yaşam döngüsü
│   │   │   ├── risk_service.py              # ← Doc 02 §2.4 risk kontrol kuralları
│   │   │   ├── strategy_service.py          # ← Doc 02 §2.5 strateji yönetimi
│   │   │   ├── ai_ml_service.py             # ← Doc 02 §2.6 model serving
│   │   │   ├── backtest_service.py          # ← Doc 02 §2.7 simülasyon
│   │   │   ├── portfolio_service.py         # ← Doc 02 §2.8 pozisyon/PnL
│   │   │   ├── notification_service.py      # ← Doc 02 §2.9 bildirim kanalları
│   │   │   └── scheduler_service.py         # ← Doc 02 §2.10 zamanlanmış görevler
│   │   │
│   │   ├── repositories/                    # Veri erişim katmanı
│   │   │   ├── __init__.py
│   │   │   ├── base.py                      # BaseRepository (generic CRUD) ← Doc 07 §12.2
│   │   │   ├── user_repository.py
│   │   │   ├── market_repository.py
│   │   │   ├── order_repository.py
│   │   │   ├── portfolio_repository.py
│   │   │   ├── strategy_repository.py
│   │   │   ├── backtest_repository.py
│   │   │   ├── risk_repository.py
│   │   │   └── notification_repository.py
│   │   │
│   │   ├── strategies/                      # Trading stratejileri
│   │   │   ├── __init__.py
│   │   │   ├── base.py                      # BaseStrategy ABC ← Doc 02 §2.5
│   │   │   ├── ma_crossover.py              # SMA Crossover ← Doc 05 §9.1
│   │   │   ├── rsi_reversal.py              # RSI Mean Reversion ← Doc 05 §9.1
│   │   │   ├── momentum_ranker.py           # Momentum Ranker ← Doc 05 §9.1
│   │   │   └── ai_trend_predictor.py        # XGBoost Trend ← Doc 05 §9.2
│   │   │
│   │   ├── indicators/                      # Teknik göstergeler
│   │   │   ├── __init__.py
│   │   │   └── momentum.py                  # RSI, MACD, Stochastic ← Doc 07 §18
│   │   │
│   │   ├── brokers/                         # Broker adaptörleri
│   │   │   ├── __init__.py
│   │   │   ├── base.py                      # AbstractBroker ← Doc 07 §17.1
│   │   │   ├── paper_broker.py              # PaperBroker ← Doc 07 §17.2
│   │   │   ├── factory.py                   # BrokerFactory ← Doc 07 §17.3
│   │   │   └── is_yatirim.py                # İş Yatırım (Faz 2) ← Doc 01 §5.1
│   │   │
│   │   ├── ml/                              # Makine öğrenmesi
│   │   │   ├── __init__.py
│   │   │   ├── features.py                  # Feature engineering ← Doc 02 §2.6
│   │   │   ├── trainer.py                   # Model training pipeline
│   │   │   ├── predictor.py                 # Model inference/serving
│   │   │   └── models/                      # Eğitilmiş model artefaktları
│   │   │       └── .gitkeep
│   │   │
│   │   ├── tasks/                           # Celery görevleri
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py                # Celery config ← Doc 07 §16
│   │   │   ├── market_tasks.py              # EOD veri çekme ← Doc 07 §16.2
│   │   │   ├── strategy_tasks.py            # Strateji sinyal üretimi
│   │   │   ├── ml_tasks.py                  # Model training/prediction
│   │   │   └── notification_tasks.py        # Email/Telegram gönderimi
│   │   │
│   │   ├── websocket/                       # WebSocket handler'lar
│   │   │   ├── __init__.py
│   │   │   └── market_stream.py             # Canlı fiyat stream ← Doc 07 §15.2
│   │   │
│   │   └── utils/                           # Yardımcılar
│   │       ├── __init__.py
│   │       ├── constants.py                 # BIST saatleri, limitler ← Doc 07 §25.1
│   │       └── formatters.py                # Para, yüzde formatters ← Doc 07 §25.2
│   │
│   ├── alembic/                             # Migrasyon dosyaları
│   │   ├── env.py                           # ← Doc 07 §20.2
│   │   ├── script.py.mako
│   │   └── versions/                        # Migrasyon dosya dizini
│   │       └── .gitkeep
│   ├── alembic.ini                          # ← Doc 07 §20.1
│   │
│   ├── scripts/                             # Yardımcı scriptler
│   │   ├── seed_symbols.py                  # BIST30 sembol/endeks seed ← Doc 07 §23
│   │   └── fetch_historical.py              # Geçmiş veri çekme
│   │
│   ├── tests/                               # Backend testleri
│   │   ├── __init__.py
│   │   ├── conftest.py                      # Fixture'lar ← Doc 07 §24
│   │   ├── test_auth.py
│   │   ├── test_market.py
│   │   ├── test_orders.py
│   │   ├── test_portfolio.py
│   │   ├── test_strategies.py
│   │   ├── test_risk.py
│   │   ├── test_backtest.py
│   │   └── test_health.py
│   │
│   ├── pyproject.toml                       # ← Doc 07 §21
│   └── Dockerfile                           # ← Doc 10 §2.1 (BUNU KULLAN)
│
├── frontend/                                # Next.js Frontend
│   ├── src/
│   │   ├── app/                             # Next.js App Router
│   │   │   ├── layout.tsx                   # Root layout ← Doc 08 §7.1
│   │   │   ├── page.tsx                     # Landing / redirect
│   │   │   ├── globals.css                  # CSS variables ← Doc 08 §2.3
│   │   │   │
│   │   │   ├── (auth)/                      # Auth layout group
│   │   │   │   ├── login/page.tsx           # ← Doc 09 §14.1
│   │   │   │   └── register/page.tsx        # ← Doc 09 §14.1 pattern
│   │   │   │
│   │   │   └── (dashboard)/                 # Dashboard layout group
│   │   │       ├── layout.tsx               # Sidebar+Header layout ← Doc 08 §7.4
│   │   │       ├── dashboard/page.tsx       # ← Doc 08 §8.2, Doc 04 §2.2
│   │   │       ├── market/
│   │   │       │   ├── page.tsx             # Piyasa listesi ← Doc 04 §2.3
│   │   │       │   └── [symbol]/page.tsx    # Sembol detay ← Doc 04 §2.3
│   │   │       ├── trends/page.tsx          # Trend analiz ← Doc 04 §2.4
│   │   │       ├── strategies/
│   │   │       │   ├── page.tsx             # Strateji listesi ← Doc 04 §2.5
│   │   │       │   ├── new/page.tsx         # Yeni strateji
│   │   │       │   └── [id]/page.tsx        # Strateji detay
│   │   │       ├── backtest/
│   │   │       │   ├── page.tsx             # Backtest ← Doc 04 §2.6
│   │   │       │   └── [id]/page.tsx        # Backtest sonuç
│   │   │       ├── portfolio/page.tsx       # Portföy ← Doc 04 §2.7
│   │   │       ├── orders/page.tsx          # Emir geçmişi
│   │   │       └── settings/page.tsx        # Ayarlar ← Doc 04 §2.8
│   │   │
│   │   ├── components/
│   │   │   ├── ui/                          # shadcn/ui ← Doc 08 §1.2
│   │   │   ├── charts/                      # Grafik bileşenler
│   │   │   │   ├── candlestick-chart.tsx    # ← Doc 08 §9.1
│   │   │   │   ├── equity-curve.tsx
│   │   │   │   ├── pnl-bar-chart.tsx
│   │   │   │   ├── allocation-pie.tsx
│   │   │   │   └── trend-heatmap.tsx
│   │   │   ├── market/
│   │   │   │   ├── symbol-table.tsx
│   │   │   │   ├── symbol-card.tsx
│   │   │   │   ├── order-book.tsx
│   │   │   │   ├── order-form.tsx
│   │   │   │   └── quote-ticker.tsx
│   │   │   ├── trends/
│   │   │   │   ├── trend-filters.tsx
│   │   │   │   ├── dip-candidate-card.tsx
│   │   │   │   ├── breakout-candidate-card.tsx
│   │   │   │   └── trend-treemap.tsx
│   │   │   ├── portfolio/
│   │   │   │   ├── position-table.tsx
│   │   │   │   ├── portfolio-summary.tsx
│   │   │   │   └── pnl-summary.tsx
│   │   │   ├── strategy/
│   │   │   │   ├── strategy-card.tsx
│   │   │   │   ├── strategy-form.tsx
│   │   │   │   └── signal-table.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── stat-card.tsx            # ← Doc 08 §8.1
│   │   │   │   ├── risk-gauge.tsx
│   │   │   │   └── recent-signals.tsx
│   │   │   ├── layout/
│   │   │   │   ├── header.tsx               # ← Doc 08 §7.6
│   │   │   │   ├── sidebar.tsx              # ← Doc 08 §7.5
│   │   │   │   ├── mobile-nav.tsx
│   │   │   │   └── notification-bell.tsx
│   │   │   ├── auth/
│   │   │   │   └── auth-guard.tsx           # ← Doc 08 §11
│   │   │   ├── providers/
│   │   │   │   ├── theme-provider.tsx       # ← Doc 08 §7.2
│   │   │   │   └── query-provider.tsx       # ← Doc 08 §7.3
│   │   │   └── shared/
│   │   │       ├── empty-state.tsx          # ← Doc 09 §10
│   │   │       ├── loading-skeleton.tsx
│   │   │       └── error-boundary.tsx
│   │   │
│   │   ├── hooks/
│   │   │   ├── use-websocket.ts             # ← Doc 08 §6.1
│   │   │   ├── use-market-data.ts           # ← Doc 08 §6.2
│   │   │   ├── use-portfolio.ts             # ← Doc 08 §6.3
│   │   │   └── use-auth.ts
│   │   │
│   │   ├── lib/
│   │   │   ├── api/
│   │   │   │   ├── client.ts                # Axios instance ← Doc 08 §3.1
│   │   │   │   ├── market.ts                # ← Doc 08 §3.2
│   │   │   │   ├── orders.ts                # ← Doc 08 §3.3
│   │   │   │   ├── portfolio.ts
│   │   │   │   ├── strategies.ts
│   │   │   │   ├── backtest.ts
│   │   │   │   ├── risk.ts
│   │   │   │   └── auth.ts
│   │   │   ├── ws/
│   │   │   │   └── market-stream.ts
│   │   │   ├── utils/
│   │   │   │   ├── formatters.ts            # ← Doc 08 §10.2
│   │   │   │   └── constants.ts
│   │   │   ├── utils.ts                     # cn() helper ← Doc 08 §10.1
│   │   │   └── validators/
│   │   │       └── schemas.ts               # Zod şemaları
│   │   │
│   │   ├── stores/
│   │   │   ├── auth-store.ts                # ← Doc 08 §5.1
│   │   │   ├── market-store.ts              # ← Doc 08 §5.2
│   │   │   └── ui-store.ts                  # ← Doc 08 §5.3
│   │   │
│   │   └── types/
│   │       ├── market.ts                    # ← Doc 08 §4.1
│   │       ├── order.ts                     # ← Doc 08 §4.2
│   │       ├── portfolio.ts                 # ← Doc 08 §4.3
│   │       ├── strategy.ts                  # ← Doc 08 §4.4
│   │       └── api.ts                       # Genel API tipleri
│   │
│   ├── public/
│   │   └── favicon.ico
│   ├── next.config.ts                       # ← Doc 08 §2.1
│   ├── tailwind.config.ts                   # ← Doc 08 §2.2
│   ├── tsconfig.json
│   ├── package.json
│   ├── components.json                      # shadcn/ui config ← Doc 08 §1.2
│   └── Dockerfile                           # ← Doc 10 §3.1
│
├── scripts/
│   └── init-db.sql                          # ← Doc 10 §1.2
│
├── .github/
│   └── workflows/
│       └── ci.yml                           # ← Doc 10 §4.1
│
├── docker-compose.yml                       # ← Doc 10 §1.1 (KÖK DİZİNDE)
├── .env.example
├── .gitignore
├── Makefile
└── README.md
```

---

## 📖 DOKÜMAN REFERİNS HARİTASI (Master)

> Bu harita, her dosyanın **hangi dokümanın hangi bölümünden** oluşturulacağını kesin olarak belirtir.

### Backend Dosya → Doküman Eşlemesi

| Dosya Yolu                               | Kaynak Doküman | Bölüm                    | Notlar                                   |
| ---------------------------------------- | -------------- | ------------------------ | ---------------------------------------- |
| `backend/app/config.py`                  | Doc 07         | §2 — Ortam Değişkenleri  | Pydantic Settings class, `.env` okuma    |
| `backend/app/database.py`                | Doc 07         | §3 — Veritabanı Bağlantı | async engine, session factory            |
| `backend/app/models/base.py`             | Doc 07         | §4.1 — ORM Model Temeli  | TimestampMixin, UUIDMixin                |
| `backend/app/models/user.py`             | Doc 07         | §4.2 — User Model        | Örnek model, diğerleri bunu takip etmeli |
| `backend/app/models/*.py` (diğer)        | Doc 03         | §2 — SQL Tablo Tanımları | Her tablo tanımını SQLAlchemy'ye çevir   |
| `backend/app/main.py`                    | Doc 07         | §5 — FastAPI App Factory | `create_app()`, lifespan, middleware     |
| `backend/app/middleware.py`              | Doc 07         | §6 — Middleware          | Request logging, rate limiting           |
| `backend/app/exceptions.py`              | Doc 07         | §7 — Exception Handling  | Custom exceptions + global handler       |
| `backend/app/core/security.py`           | Doc 07         | §8 — Güvenlik            | JWT encode/decode, password hash         |
| `backend/app/dependencies.py`            | Doc 07         | §9 — Dependencies        | `get_current_user`, `require_role`       |
| `backend/app/api/router.py`              | Doc 07         | §10.1 — API Router       | Ana v1 router, prefix yapısı             |
| `backend/app/api/health.py`              | Doc 07         | §10.2 — Health Check     | DB, Redis, Kafka kontrol                 |
| `backend/app/api/v1/auth.py`             | Doc 07         | §10.3 — Auth Router      | Register, login, refresh, me, logout     |
| `backend/app/api/v1/market.py`           | Doc 02         | §2.2 + Doc 03 §3.3       | Endpoint listesi + response JSON         |
| `backend/app/api/v1/orders.py`           | Doc 02         | §2.3 + Doc 03 §3.4       | Emir CRUD + yaşam döngüsü                |
| `backend/app/api/v1/portfolio.py`        | Doc 02         | §2.8 + Doc 03 §3.5       | Pozisyon, PnL, allocation                |
| `backend/app/api/v1/strategies.py`       | Doc 02         | §2.5                     | Strateji CRUD + aktivasyon               |
| `backend/app/api/v1/backtest.py`         | Doc 02         | §2.7                     | Backtest çalıştır, sonuç sorgula         |
| `backend/app/api/v1/risk.py`             | Doc 02         | §2.4 + Doc 03 §3.7       | Risk kuralları, durum, uyarılar          |
| `backend/app/api/v1/analysis.py`         | Doc 03         | §3.6                     | Trend analiz, dip/kırılım                |
| `backend/app/schemas/common.py`          | Doc 07         | §11.1                    | APIResponse, PaginationMeta              |
| `backend/app/schemas/auth.py`            | Doc 07         | §11.2                    | Register, Login, Token şemaları          |
| `backend/app/schemas/*.py` (diğer)       | Doc 03         | §4 — Pydantic Modelleri  | Tüm request/response şemaları            |
| `backend/app/services/*.py`              | Doc 02         | §2.1–§2.10               | Her servisin iş mantığı                  |
| `backend/app/repositories/base.py`       | Doc 07         | §12.2                    | Generic CRUD repository                  |
| `backend/app/core/redis_client.py`       | Doc 07         | §13                      | RedisManager singleton                   |
| `backend/app/core/rate_limiter.py`       | Doc 07         | §14                      | Redis tabanlı rate limiter               |
| `backend/app/core/websocket_manager.py`  | Doc 07         | §15.1                    | Channel-based WS yönetimi                |
| `backend/app/websocket/market_stream.py` | Doc 07         | §15.2                    | WS endpoint handler                      |
| `backend/app/tasks/celery_app.py`        | Doc 07         | §16.1                    | Celery config, beat schedule             |
| `backend/app/tasks/market_tasks.py`      | Doc 07         | §16.2                    | EOD data fetch task                      |
| `backend/app/brokers/base.py`            | Doc 07         | §17.1                    | AbstractBroker interface                 |
| `backend/app/brokers/paper_broker.py`    | Doc 07         | §17.2                    | Simülasyon broker                        |
| `backend/app/brokers/factory.py`         | Doc 07         | §17.3                    | Broker factory                           |
| `backend/app/indicators/momentum.py`     | Doc 07         | §18                      | RSI, MACD, Stochastic                    |
| `backend/app/logging_config.py`          | Doc 07         | §19                      | structlog setup                          |
| `backend/alembic.ini`                    | Doc 07         | §20.1                    | Alembic yapılandırma                     |
| `backend/alembic/env.py`                 | Doc 07         | §20.2                    | Migration env                            |
| `backend/pyproject.toml`                 | Doc 07         | §21                      | Poetry bağımlılıklar                     |
| `backend/Dockerfile`                     | Doc 10         | §2.1                     | Multi-stage build                        |
| `backend/scripts/seed_symbols.py`        | Doc 07         | §23                      | BIST30 seed data                         |
| `backend/tests/conftest.py`              | Doc 07         | §24                      | Test fixture'ları                        |
| `backend/app/utils/constants.py`         | Doc 07         | §25.1                    | Sabitler                                 |
| `backend/app/utils/formatters.py`        | Doc 07         | §25.2                    | Formatlama                               |
| `backend/app/strategies/base.py`         | Doc 02         | §2.5                     | BaseStrategy abstract class              |

### Ek Referanslar — Sprint Görevlerinde Kullanılacak

| Konu                                                        | Kaynak Doküman | Bölüm     | Kullanım Yeri                                                                                            |
| ----------------------------------------------------------- | -------------- | --------- | -------------------------------------------------------------------------------------------------------- |
| TimescaleDB hypertable + aggregate tanımı                   | Doc 03         | §2.16     | Faz 0 — Alembic migration sonrası raw SQL olarak çalıştır (`init-db.sql` içine ekle veya ayrı migration) |
| WebSocket API sözleşmesi (subscription, message formatları) | Doc 03         | §3.8      | Sprint 1.1 — WS endpoint implemente ederken request/response JSON formatını baz al                       |
| Kafka event tipleri ve şemaları                             | Doc 03         | §5.1–§5.2 | Sprint 2.3 — Event-driven akışlar implemente ederken (strateji → emir, bildirimler)                      |
| HTTP hata kodları tablosu                                   | Doc 03         | §3.2      | Faz 0 — `exceptions.py` oluştururken hata kodu eşlemesini baz al                                         |
| Veri akış diyagramları                                      | Doc 02         | §3.1–§3.3 | Tüm fazlar — Gerçek zamanlı veri, emir, backtest akışlarında referans                                    |
| Güvenlik mimarisi detayları                                 | Doc 02         | §6        | Sprint 1.1 — Auth service, API key rotation, audit logging                                               |
| Erişilebilirlik (WCAG 2.1 AA)                               | Doc 09         | §13       | Tüm frontend görevleri — Her bileşende a11y kontrol                                                      |
| Responsive tasarım kuralları                                | Doc 09         | §12       | Tüm frontend görevleri — Breakpoint ve layout davranışları                                               |
| Dashboard tasarım detayları                                 | Doc 09         | §14.2     | Sprint 1.1 — Dashboard sayfası oluştururken                                                              |
| Piyasa detay tasarım detayları                              | Doc 09         | §14.3     | Sprint 1.2 — Sembol detay sayfası oluştururken                                                           |

### Frontend Dosya → Doküman Eşlemesi

| Dosya Yolu                                             | Kaynak Doküman | Bölüm     | Notlar                          |
| ------------------------------------------------------ | -------------- | --------- | ------------------------------- |
| `frontend/next.config.ts`                              | Doc 08         | §2.1      | Image domains, env              |
| `frontend/tailwind.config.ts`                          | Doc 08         | §2.2      | Custom theme, animations        |
| `frontend/src/app/globals.css`                         | Doc 08         | §2.3      | CSS variables (dark/light)      |
| `frontend/src/lib/api/client.ts`                       | Doc 08         | §3.1      | Axios + interceptors + refresh  |
| `frontend/src/lib/api/market.ts`                       | Doc 08         | §3.2      | Market API fonksiyonları        |
| `frontend/src/lib/api/orders.ts`                       | Doc 08         | §3.3      | Order API fonksiyonları         |
| `frontend/src/types/market.ts`                         | Doc 08         | §4.1      | TS tip tanımları                |
| `frontend/src/types/order.ts`                          | Doc 08         | §4.2      | TS tip tanımları                |
| `frontend/src/types/portfolio.ts`                      | Doc 08         | §4.3      | TS tip tanımları                |
| `frontend/src/types/strategy.ts`                       | Doc 08         | §4.4      | TS tip tanımları                |
| `frontend/src/stores/auth-store.ts`                    | Doc 08         | §5.1      | Zustand auth store              |
| `frontend/src/stores/market-store.ts`                  | Doc 08         | §5.2      | Zustand market store            |
| `frontend/src/stores/ui-store.ts`                      | Doc 08         | §5.3      | Zustand UI store                |
| `frontend/src/hooks/use-websocket.ts`                  | Doc 08         | §6.1      | Native WebSocket + reconnect    |
| `frontend/src/hooks/use-market-data.ts`                | Doc 08         | §6.2      | TanStack Query hooks            |
| `frontend/src/hooks/use-portfolio.ts`                  | Doc 08         | §6.3      | Portfolio hooks                 |
| `frontend/src/app/layout.tsx`                          | Doc 08         | §7.1      | Root layout                     |
| `frontend/src/components/providers/theme-provider.tsx` | Doc 08         | §7.2      | next-themes                     |
| `frontend/src/components/providers/query-provider.tsx` | Doc 08         | §7.3      | TanStack provider               |
| `frontend/src/app/(dashboard)/layout.tsx`              | Doc 08         | §7.4      | Dashboard layout                |
| `frontend/src/components/layout/sidebar.tsx`           | Doc 08         | §7.5      | Nav sidebar                     |
| `frontend/src/components/layout/header.tsx`            | Doc 08         | §7.6      | Header                          |
| `frontend/src/components/dashboard/stat-card.tsx`      | Doc 08         | §8.1      | Stat card bileşeni              |
| `frontend/src/app/(dashboard)/dashboard/page.tsx`      | Doc 08         | §8.2      | Dashboard page                  |
| `frontend/src/components/charts/candlestick-chart.tsx` | Doc 08         | §9.1      | TradingView chart               |
| `frontend/src/lib/utils.ts`                            | Doc 08         | §10.1     | `cn()` helper                   |
| `frontend/src/lib/utils/formatters.ts`                 | Doc 08         | §10.2     | Para, tarih, PnL                |
| `frontend/src/components/auth/auth-guard.tsx`          | Doc 08         | §11       | Auth guard                      |
| `frontend/Dockerfile`                                  | Doc 10         | §3.1      | Multi-stage build               |
| Tüm sayfa wireframe'leri                               | Doc 04         | §2.2–§2.8 | ASCII wireframe'ler             |
| Tüm tasarım token'ları / stiller                       | Doc 09         | §2–§15    | Token, component, a11y          |
| Empty state bileşeni                                   | Doc 09         | §10       | EmptyState component + örnekler |
| Toast/bildirim stili                                   | Doc 09         | §11       | Sonner kullanımı                |

### Altyapı Dosya → Doküman Eşlemesi

| Dosya Yolu                 | Kaynak Doküman | Bölüm |
| -------------------------- | -------------- | ----- |
| `docker-compose.yml`       | Doc 10         | §1.1  |
| `scripts/init-db.sql`      | Doc 10         | §1.2  |
| `.github/workflows/ci.yml` | Doc 10         | §4.1  |

---

## 🗺️ GELİŞTİRME SIRASI — FAZ BAZLI MASTER YOL HARİTASI

### Faz 0 — Altyapı Kurulumu (Hafta 1-2)

> **Amaç:** Proje iskeleti, Docker ortamı, veritabanı, temel backend ve frontend projelerinin çalışır hale gelmesi.

#### Adım 0.1 — Proje Kök Yapısı

```
EYLEM: Proje kök dizinini oluştur
DOSYALAR:
  - docker-compose.yml          ← Doc 10 §1.1'den kopyala
  - scripts/init-db.sql         ← Doc 10 §1.2'den kopyala
  - .github/workflows/ci.yml    ← Doc 10 §4.1'den kopyala
  - .env.example                ← Mevcut dosya zaten var, kontrol et
  - .gitignore                  ← Mevcut dosya zaten var, kontrol et
  - Makefile                    ← Mevcut dosyayı güncelle (docker-compose yollarını düzelt)
  - README.md                   ← Mevcut, güncelleme gerekmiyor

DOĞRULAMA:
  ✓ docker-compose.yml geçerli YAML
  ✓ docker compose config komutu hata vermeden çalışır
```

#### Adım 0.2 — Backend Projesi Oluşturma

```
EYLEM: Backend dizin yapısını ve çekirdek dosyaları oluştur
KOMUTLAR:
  mkdir backend
  cd backend
  poetry init --name bist-robogo-backend --python "^3.12"
  (Sonra pyproject.toml'u Doc 07 §21'den gelen tam içerikle değiştir)
  poetry install

DOSYALAR (sırasıyla oluştur):
  1.  app/__init__.py                    ← Boş
  2.  app/config.py                      ← Doc 07 §2
  3.  app/logging_config.py              ← Doc 07 §19
  4.  app/database.py                    ← Doc 07 §3
  5.  app/models/base.py                 ← Doc 07 §4.1
  6.  app/models/user.py                 ← Doc 07 §4.2
  7.  app/models/*.py (market, broker, strategy, order, portfolio, risk, backtest, notification, audit)
                                         ← Doc 03 §2 SQL şemalarını SQLAlchemy'ye çevir
                                         ← Doc 07 §4.2 user.py'yi şablon olarak kullan
  8.  app/models/__init__.py             ← Doc 07 §4.3 — tüm modelleri re-export
  9.  app/exceptions.py                  ← Doc 07 §7 + Doc 03 §3.2 (hata kodları tablosu)
  10. app/core/security.py               ← Doc 07 §8
  11. app/core/redis_client.py           ← Doc 07 §13
  12. app/core/rate_limiter.py           ← Doc 07 §14
  13. app/core/websocket_manager.py      ← Doc 07 §15.1
  14. app/middleware.py                   ← Doc 07 §6
  15. app/dependencies.py                ← Doc 07 §9
  16. app/schemas/common.py              ← Doc 07 §11.1
  17. app/schemas/auth.py                ← Doc 07 §11.2
  18. app/schemas/*.py (diğer)           ← Doc 03 §4 Pydantic modelleri
  19. app/repositories/base.py           ← Doc 07 §12.2
  20. app/api/health.py                  ← Doc 07 §10.2
  21. app/api/v1/auth.py                 ← Doc 07 §10.3
  22. app/api/router.py                  ← Doc 07 §10.1
  23. app/main.py                        ← Doc 07 §5 (exception handler'ları da EKLE!)
  24. app/utils/constants.py             ← Doc 07 §25.1
  25. app/utils/formatters.py            ← Doc 07 §25.2

DOĞRULAMA:
  ✓ cd backend && poetry run python -c "from app.main import app; print('OK')"
  ✓ poetry run ruff check .
  ✓ poetry run mypy . --ignore-missing-imports
```

#### Adım 0.3 — Alembic Migrasyon

```
EYLEM: Alembic yapılandır ve ilk migrasyonu oluştur
DOSYALAR:
  1. alembic.ini                         ← Doc 07 §20.1
  2. alembic/env.py                      ← Doc 07 §20.2
  3. alembic/script.py.mako              ← Standart Alembic şablonu

KOMUTLAR:
  cd backend
  poetry run alembic revision --autogenerate -m "initial_schema"
  (Docker postgres çalışır durumda olmalı)
  poetry run alembic upgrade head

ÖNEMLİ — TimescaleDB Hypertable Kurulumu:
  Alembic migration sonrasında, TimescaleDB extension ve hypertable'ları oluştur:
  - scripts/init-db.sql dosyasını çalıştır (Doc 10 §1.2)
  - VEYA ayrı bir Alembic migration içinde raw SQL çalıştır
  - Kaynak: Doc 03 §2.16 — ohlcv_1m, ohlcv_1d, ohlcv_1w, ticks tabloları
  - Bu tablolar normal ORM model DEĞİL — hypertable + continuous aggregate + compression policy gerektirir

DOĞRULAMA:
  ✓ Tüm 16+ tablo veritabanında oluşmuş
  ✓ TimescaleDB hypertable'lar oluşmuş (ohlcv_1m, ohlcv_1d, ohlcv_1w, ticks)
  ✓ alembic_version tablosu mevcut
```

#### Adım 0.4 — Backend İlk Çalıştırma

```
EYLEM: Backend'i çalıştır ve health check test et
KOMUTLAR:
  docker compose up -d postgres redis
  cd backend
  poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

DOĞRULAMA:
  ✓ GET http://localhost:8000/health → 200 OK
  ✓ GET http://localhost:8000/docs → Swagger UI açılır
  ✓ POST http://localhost:8000/api/v1/auth/register → 201 (test verisi ile)
  ✓ POST http://localhost:8000/api/v1/auth/login → 200 (token döner)
```

#### Adım 0.5 — Frontend Projesi Oluşturma

```
EYLEM: Next.js projesi oluştur ve yapılandır
KOMUTLAR:
  npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir
  cd frontend
  pnpm add axios zustand @tanstack/react-query @tanstack/react-query-devtools
  pnpm add next-themes sonner lightweight-charts recharts
  pnpm add -D @types/node

  # shadcn/ui kurulumu (Doc 08 §1.2'deki component listesini kur)
  npx shadcn@latest init
  npx shadcn@latest add button card input label select table tabs badge progress dialog sheet dropdown-menu avatar separator skeleton tooltip popover command switch textarea scroll-area slider

  # NOT: socket.io-client KURMA — native WebSocket kullanılıyor

DOSYALAR (sırasıyla oluştur):
  1. next.config.ts                      ← Doc 08 §2.1
  2. tailwind.config.ts                  ← Doc 08 §2.2
  3. src/app/globals.css                 ← Doc 08 §2.3
  4. src/lib/utils.ts                    ← Doc 08 §10.1
  5. src/lib/utils/formatters.ts         ← Doc 08 §10.2
  6. src/types/market.ts                 ← Doc 08 §4.1
  7. src/types/order.ts                  ← Doc 08 §4.2
  8. src/types/portfolio.ts              ← Doc 08 §4.3
  9. src/types/strategy.ts               ← Doc 08 §4.4
  10. src/types/api.ts                   ← Genel API response tipleri
  11. src/lib/api/client.ts              ← Doc 08 §3.1
  12. src/lib/api/auth.ts                ← Doc 08 §3.1 pattern ile
  13. src/lib/api/market.ts              ← Doc 08 §3.2
  14. src/lib/api/orders.ts              ← Doc 08 §3.3
  15. src/lib/api/portfolio.ts           ← pattern takip et
  16. src/lib/api/strategies.ts          ← pattern takip et
  17. src/lib/api/backtest.ts            ← pattern takip et
  18. src/lib/api/risk.ts                ← pattern takip et
  19. src/stores/auth-store.ts           ← Doc 08 §5.1
  20. src/stores/market-store.ts         ← Doc 08 §5.2
  21. src/stores/ui-store.ts             ← Doc 08 §5.3
  22. src/hooks/use-websocket.ts         ← Doc 08 §6.1
  23. src/hooks/use-market-data.ts       ← Doc 08 §6.2
  24. src/hooks/use-portfolio.ts         ← Doc 08 §6.3
  25. src/components/providers/theme-provider.tsx   ← Doc 08 §7.2
  26. src/components/providers/query-provider.tsx   ← Doc 08 §7.3
  27. src/app/layout.tsx                 ← Doc 08 §7.1
  28. src/components/auth/auth-guard.tsx  ← Doc 08 §11
  29. src/components/shared/empty-state.tsx ← Doc 09 §10

DOĞRULAMA:
  ✓ cd frontend && pnpm build → hatasız tamamlanır
  ✓ pnpm dev → localhost:3000 açılır
  ✓ pnpm lint → hata yok
```

#### Adım 0.6 — Docker Compose Entegrasyonu

```
EYLEM: Tüm servisleri Docker ile ayağa kaldır
DOSYALAR:
  1. backend/Dockerfile                  ← Doc 10 §2.1
  2. frontend/Dockerfile                 ← Doc 10 §3.1

KOMUTLAR:
  docker compose up -d --build

DOĞRULAMA:
  ✓ docker compose ps → tüm servisler "healthy" veya "running"
  ✓ http://localhost:8000/health → 200
  ✓ http://localhost:3000 → Next.js sayfası
  ✓ docker compose logs backend → hata yok
  ✓ docker compose logs frontend → hata yok
```

---

### Faz 1 — MVP Temel Özellikler (Hafta 3-8)

#### Sprint 1.1 — Auth + Dashboard Temeli (Hafta 3-4)

| #      | Görev                                    | Dosya(lar)                                            | Kaynak                     | Doğrulama                                    |
| ------ | ---------------------------------------- | ----------------------------------------------------- | -------------------------- | -------------------------------------------- |
| 1.1.1  | Auth service implementasyonu             | `services/auth_service.py`                            | Doc 02 §2.1                | Register, login, refresh çalışır             |
| 1.1.2  | Auth repository                          | `repositories/user_repository.py`                     | Doc 07 §12.2 pattern       | CRUD testleri geçer                          |
| 1.1.3  | Auth API tamamlama (refresh_token impl.) | `api/v1/auth.py`                                      | Doc 07 §10.3               | Token refresh çalışır                        |
| 1.1.4  | Login sayfası (frontend)                 | `(auth)/login/page.tsx`                               | Doc 09 §14.1 wireframe     | Login akışı tamamlanır                       |
| 1.1.5  | Register sayfası (frontend)              | `(auth)/register/page.tsx`                            | Doc 09 §14.1 pattern       | Kayıt akışı tamamlanır                       |
| 1.1.6  | Dashboard layout (sidebar + header)      | `(dashboard)/layout.tsx`, `sidebar.tsx`, `header.tsx` | Doc 08 §7.4-§7.6           | Sidebar navigasyon çalışır                   |
| 1.1.7  | Dashboard stat kartları                  | `dashboard/stat-card.tsx`, `dashboard/page.tsx`       | Doc 08 §8.1-§8.2           | 5 istatistik kartı görünür                   |
| 1.1.8  | Auth guard middleware                    | `auth-guard.tsx`                                      | Doc 08 §11                 | Giriş yapmadan dashboard'a erişim engellenir |
| 1.1.9  | Seed data çalıştır                       | `scripts/seed_symbols.py`                             | Doc 07 §23                 | BIST30 + endeksler DB'de                     |
| 1.1.10 | Backend birim testleri                   | `tests/test_auth.py`, `tests/test_health.py`          | Doc 07 §24 (conftest)      | pytest geçer                                 |
| 1.1.11 | WebSocket endpoint                       | `websocket/market_stream.py`                          | Doc 07 §15.2 + Doc 03 §3.8 | WS bağlantısı kurulur                        |
| 1.1.12 | Notification bell (placeholder)          | `layout/notification-bell.tsx`                        | Doc 09 ikon kılavuzu       | Bell ikonu header'da                         |

#### Sprint 1.2 — Piyasa Verisi + Grafik (Hafta 5-6)

| #      | Görev                              | Dosya(lar)                                          | Kaynak                    | Doğrulama                             |
| ------ | ---------------------------------- | --------------------------------------------------- | ------------------------- | ------------------------------------- |
| 1.2.1  | Market data service                | `services/market_data_service.py`                   | Doc 02 §2.2               | Sembol listesi ve OHLCV verilir       |
| 1.2.2  | Market API endpoints               | `api/v1/market.py`                                  | Doc 02 §2.2 + Doc 03 §3.3 | GET /symbols, /ohlcv, /quotes çalışır |
| 1.2.3  | Market schemas                     | `schemas/market.py`                                 | Doc 03 §4                 | Response validation geçer             |
| 1.2.4  | Market repository                  | `repositories/market_repository.py`                 | Doc 07 §12.2 pattern      | OHLCV query çalışır                   |
| 1.2.5  | Piyasa listesi sayfası             | `market/page.tsx`, `market/symbol-table.tsx`        | Doc 04 §2.3 wireframe     | Sembol tablosu görünür                |
| 1.2.6  | Sembol detay sayfası               | `market/[symbol]/page.tsx`                          | Doc 04 §2.3 wireframe     | Grafik + göstergeler görünür          |
| 1.2.7  | Candlestick chart                  | `charts/candlestick-chart.tsx`                      | Doc 08 §9.1               | TradingView chart render eder         |
| 1.2.8  | Quote ticker bileşeni              | `market/quote-ticker.tsx`                           | Doc 09 §7.2 fiyat flash   | Fiyat animasyonu çalışır              |
| 1.2.9  | Endeks seçici (BIST30/100/Katılım) | `market/page.tsx` içinde filtre                     | Doc 04 §2.3               | Endeks filtreleme çalışır             |
| 1.2.10 | WebSocket canlı fiyat              | `hooks/use-websocket.ts` + `stores/market-store.ts` | Doc 08 §6.1               | WS ile fiyat güncellenir              |
| 1.2.11 | Teknik gösterge backend hesaplama  | `indicators/momentum.py`                            | Doc 07 §18                | RSI, MACD doğru hesaplanır            |
| 1.2.12 | Symbol-card bileşeni               | `market/symbol-card.tsx`                            | Doc 09 §8.2 Card pattern  | Kart tasarımı tutarlı                 |
| 1.2.13 | Loading skeletonları               | `shared/loading-skeleton.tsx`                       | Doc 09 §7.3               | Her sayfa skeleton gösterir           |

#### Sprint 1.3 — Paper Trading + Portföy (Hafta 7-8)

| #      | Görev                            | Dosya(lar)                      | Kaynak                    | Doğrulama                                |
| ------ | -------------------------------- | ------------------------------- | ------------------------- | ---------------------------------------- |
| 1.3.1  | Trading service (paper mode)     | `services/trading_service.py`   | Doc 02 §2.3               | Paper emir gönderilebilir                |
| 1.3.2  | Paper broker adapter             | `brokers/paper_broker.py`       | Doc 07 §17.2              | Emir simüle edilir                       |
| 1.3.3  | Order API endpoints              | `api/v1/orders.py`              | Doc 02 §2.3 + Doc 03 §3.4 | CRUD çalışır                             |
| 1.3.4  | Order schemas                    | `schemas/order.py`              | Doc 03 §4                 | Validation geçer                         |
| 1.3.5  | Order form bileşeni              | `market/order-form.tsx`         | Doc 04 §2.3 wireframe     | Form gönderilir                          |
| 1.3.6  | Portfolio service                | `services/portfolio_service.py` | Doc 02 §2.8               | Pozisyon + PnL hesaplanır                |
| 1.3.7  | Portfolio API endpoints          | `api/v1/portfolio.py`           | Doc 02 §2.8 + Doc 03 §3.5 | Summary, positions çalışır               |
| 1.3.8  | Portföy sayfası                  | `portfolio/page.tsx`            | Doc 04 §2.7 wireframe     | Pozisyon tablosu + PnL görünür           |
| 1.3.9  | Position-table bileşeni          | `portfolio/position-table.tsx`  | Doc 09 §8.4 tablo stili   | Tablo tutarlı stilde                     |
| 1.3.10 | Emir geçmişi sayfası             | `orders/page.tsx`               | Doc 04 wireframe          | Emirler listelenir                       |
| 1.3.11 | Risk service (temel kurallar)    | `services/risk_service.py`      | Doc 02 §2.4               | Maks pozisyon, maks günlük zarar kontrol |
| 1.3.12 | Risk API endpoints               | `api/v1/risk.py`                | Doc 03 §3.7               | Risk status JSON döner                   |
| 1.3.13 | Dashboard gerçek veri bağlantısı | `dashboard/page.tsx` güncelle   | Doc 08 §8.2               | Dashboard API'den veri çeker             |
| 1.3.14 | Error boundary                   | `shared/error-boundary.tsx`     | Doc 08 §7 pattern         | Hata durumları graceful handle           |

---

### Faz 2 — Genişletme (Hafta 9-14)

#### Sprint 2.1 — Trend Analiz + Strateji (Hafta 9-10)

| #      | Görev                                    | Dosya(lar)                                                     | Kaynak                        | Doğrulama                             |
| ------ | ---------------------------------------- | -------------------------------------------------------------- | ----------------------------- | ------------------------------------- |
| 2.1.1  | Trend analiz algoritması (dip + kırılım) | `services/ai_ml_service.py` (veya ayrı modül)                  | Doc 02 §2.6 + Doc 03 §3.6     | Dip ve kırılım adayları tespit edilir |
| 2.1.2  | Trend analiz API                         | `api/v1/analysis.py`                                           | Doc 03 §3.6                   | JSON response doğru formattta         |
| 2.1.3  | Trend analiz sayfası                     | `trends/page.tsx`                                              | Doc 04 §2.4 (ÖNE ÇIKAN EKRAN) | Dip/kırılım kartları görünür          |
| 2.1.4  | Dip & kırılım candidate kartları         | `trends/dip-candidate-card.tsx`, `breakout-candidate-card.tsx` | Doc 04 §2.4 + Doc 09 §8       | Kart stili tutarlı                    |
| 2.1.5  | Trend treemap                            | `trends/trend-treemap.tsx`                                     | Doc 04 §2.4                   | Isı haritası render eder              |
| 2.1.6  | Strategy engine base class               | `strategies/base.py`                                           | Doc 02 §2.5 abstract class    | ABC import edilebilir                 |
| 2.1.7  | MA Crossover stratejisi                  | `strategies/ma_crossover.py`                                   | Doc 05 §9.1                   | Sinyal üretir                         |
| 2.1.8  | RSI Reversal stratejisi                  | `strategies/rsi_reversal.py`                                   | Doc 05 §9.1                   | Sinyal üretir                         |
| 2.1.9  | Strategy service                         | `services/strategy_service.py`                                 | Doc 02 §2.5                   | Strateji CRUD + activate              |
| 2.1.10 | Strategy API endpoints                   | `api/v1/strategies.py`                                         | Doc 02 §2.5                   | CRUD çalışır                          |

#### Sprint 2.2 — Backtest Motoru (Hafta 11-12)

| #     | Görev                            | Dosya(lar)                     | Kaynak                         | Doğrulama                    |
| ----- | -------------------------------- | ------------------------------ | ------------------------------ | ---------------------------- |
| 2.2.1 | Backtest core simülasyon döngüsü | `services/backtest_service.py` | Doc 02 §2.7                    | Geçmiş veri üzerinde çalışır |
| 2.2.2 | Slippage + komisyon simülasyonu  | `services/backtest_service.py` | Doc 02 §2.7                    | Sonuçlara etki eder          |
| 2.2.3 | Performans metrikleri hesaplama  | `services/backtest_service.py` | Doc 02 §2.7 (12 metrik)        | Sharpe, Sortino vb. doğru    |
| 2.2.4 | Backtest API endpoints           | `api/v1/backtest.py`           | Doc 02 §2.7                    | Run + results çalışır        |
| 2.2.5 | Celery backtest task             | `tasks/backtest_tasks.py`      | Doc 07 §16 pattern             | Async çalışır                |
| 2.2.6 | Backtest sayfası                 | `backtest/page.tsx`            | Doc 04 §2.6 wireframe          | Config + sonuçlar görünür    |
| 2.2.7 | Equity curve bileşeni            | `charts/equity-curve.tsx`      | Doc 09 §15 grafik standartları | Strateji vs Buy&Hold         |
| 2.2.8 | Backtest sonuç sayfası           | `backtest/[id]/page.tsx`       | Doc 04 §2.6                    | Detaylı metrikler görünür    |

#### Sprint 2.3 — Broker + Bildirimler (Hafta 13-14)

| #      | Görev                          | Dosya(lar)                             | Kaynak                          | Doğrulama                      |
| ------ | ------------------------------ | -------------------------------------- | ------------------------------- | ------------------------------ |
| 2.3.1  | Broker adapter interface       | `brokers/base.py` (refine)             | Doc 07 §17.1                    | Interface temiz                |
| 2.3.2  | Gerçek emir gönderme altyapısı | `services/trading_service.py` güncelle | Doc 02 §2.3                     | Broker adapter ile emir gönder |
| 2.3.3  | Notification service           | `services/notification_service.py`     | Doc 02 §2.9                     | Email + in-app çalışır         |
| 2.3.4  | Email gönderim (SMTP)          | `tasks/notification_tasks.py`          | Doc 02 §2.9                     | Email gider                    |
| 2.3.5  | Telegram bot entegrasyonu      | `tasks/notification_tasks.py`          | Doc 02 §2.9                     | Telegram mesaj gönderilir      |
| 2.3.6  | Strateji yönetim sayfası       | `strategies/page.tsx`                  | Doc 04 §2.5 wireframe           | Strateji listesi görünür       |
| 2.3.7  | Strateji → otomatik emir akışı | `tasks/strategy_tasks.py`              | Doc 02 §2.5 + 2.3 + Doc 03 §5.1 | Sinyal → risk kontrol → emir   |
| 2.3.8  | Celery beat schedule           | `tasks/celery_app.py` güncelle         | Doc 07 §16 + Doc 02 §2.10       | Scheduled task'ler çalışır     |
| 2.3.9  | Risk manager tam kurallar      | `services/risk_service.py` güncelle    | Doc 02 §2.4 (9 kural)           | Tüm kurallar enforce edilir    |
| 2.3.10 | Settings sayfası               | `settings/page.tsx`                    | Doc 04 §2.8 wireframe           | Tab'lar çalışır                |

---

### Faz 3 — AI ve Otomasyon (Hafta 15-22)

| #   | Görev                          | Kaynak      | Doğrulama                          |
| --- | ------------------------------ | ----------- | ---------------------------------- |
| 3.1 | Feature engineering pipeline   | Doc 02 §2.6 | 50+ feature üretilir               |
| 3.2 | XGBoost Trend Classifier       | Doc 05 §9.2 | Model eğitilir, MLflow'da loglanır |
| 3.3 | Dip Detector (Random Forest)   | Doc 05 §9.2 | Model accuracy > %60               |
| 3.4 | MLflow experiment tracking     | Doc 02 §2.6 | Experiment'lar izlenebilir         |
| 3.5 | ONNX model export + serving    | Doc 02 §2.6 | Inference < 50ms                   |
| 3.6 | AI Trend Predictor stratejisi  | Doc 05 §9.2 | Production'da sinyal üretir        |
| 3.7 | Optuna parametre optimizasyonu | Doc 05 §5.2 | En iyi parametreler bulunur        |
| 3.8 | Walk-forward validation        | Doc 05 §5.2 | Out-of-sample performans pozitif   |

### Faz 4 — Ölçekleme (Hafta 23+)

| #   | Görev                           | Kaynak      | Doğrulama                |
| --- | ------------------------------- | ----------- | ------------------------ |
| 4.1 | Kubernetes deployment           | Doc 02 §5.2 | K8s cluster'da çalışır   |
| 4.2 | Prometheus + Grafana monitoring | Doc 02 §7   | Dashboard'lar çalışır    |
| 4.3 | Sentry error tracking           | Doc 01 §4   | Hatalar yakalanır        |
| 4.4 | Multi-broker desteği            | Doc 01 §5.1 | 2+ broker entegre        |
| 4.5 | Model drift monitoring          | Doc 05 §5.2 | Drift tespit edilir      |
| 4.6 | Performans optimizasyonu        | Doc 01 §9   | SLA hedefleri karşılanır |

---

## ✅ DOĞRULAMA KONTROL LİSTESİ

### Her Adım Sonrası Çalıştırılacak Kontroller

#### Backend Kontrolleri

```bash
# Syntax ve stil kontrolü
cd backend
poetry run ruff check .
poetry run ruff format --check .

# Tip kontrolü
poetry run mypy . --ignore-missing-imports

# Testler
poetry run pytest -v --cov=app --cov-report=term-missing

# Migration kontrolü
poetry run alembic check  # Pending migration var mı

# Uygulama başlatma testi
poetry run python -c "from app.main import app; print('Import OK')"
```

#### Frontend Kontrolleri

```bash
cd frontend

# TypeScript kontrolü
pnpm tsc --noEmit

# Lint
pnpm lint

# Build (en önemli kontrol)
pnpm build

# Test (varsa)
pnpm test
```

#### Docker Kontrolleri

```bash
# Tüm servisleri başlat
docker compose up -d --build

# Servis durumlarını kontrol et
docker compose ps

# Logları kontrol et (hata olmamalı)
docker compose logs backend --tail=50
docker compose logs frontend --tail=50

# API erişilebilirlik
curl -s http://localhost:8000/health | jq .
curl -s http://localhost:3000 | head -20
```

---

## 🎨 TASARIM KURALLARI (Özet)

> Detaylar: Doc 09 (Tasarım Sistemi)

### Renk Kuralları

- **Kâr (profit):** `hsl(142 72% 45%)` — yeşil
- **Zarar (loss):** `hsl(0 84% 60%)` — kırmızı
- **Primary:** `hsl(217 91% 60%)` — mavi
- **Background (dark):** `hsl(224 71% 4%)` — koyu lacivert
- **Fiyatlar:** HER ZAMAN `font-mono tabular-nums`

### Tipografi Kuralları

- **Genel metin:** Inter
- **Sayısal veri:** JetBrains Mono
- **Fiyatlar:** `font-mono tabular-nums font-semibold`
- **PnL:** `font-mono tabular-nums font-medium` + profit/loss rengi
- **Tablo başlık:** `text-xs font-medium text-muted-foreground uppercase tracking-wider`

### Bileşen Kuralları

- Kartlar: `rounded-lg`, `border`, dark tema'da gölge yerine border
- Animasyonlar: max 300ms, ease-out
- Loading: Skeleton component
- Empty state: her sayfada tanımlı (Doc 09 §10)
- Toast: Sonner, sağ üstte, 3-5sn (Doc 09 §11)
- İkonlar: Sadece Lucide React (Doc 09 §9)

---

## 📋 KRİTİK NOTLAR

### Doküman Kodlarla Çelişirse

1. **Doküman 11 (bu döküman) > Doküman 10 > Doküman 07/08 > Doküman 02/03** — öncelik sırası
2. Bu dokümandaki "Bilinen Tutarsızlıklar ve Çözümleri" tablosundaki kararlar kesindir
3. Dokümanlar arası çelişkide bu dokümandaki harita/tablo geçerlidir

### ORM Model Oluşturma Kuralı

Doc 07'de sadece `user.py` modeli tam kod olarak verilmiştir. Diğer modeller için:

1. **Doc 03 §2'deki SQL CREATE TABLE** tanımını temel al
2. **Doc 07 §4.1'deki `TimestampMixin`, `UUIDMixin`** mixin'lerini uygula
3. **Doc 07 §4.2'deki `user.py`** yapısını şablon olarak kullan
4. Her model dosyasına `# Source: Doc 03 §2 — {tablo_adı}` yorumunu ekle

### Service Katmanı Oluşturma Kuralı

Doc 07'de sadece generic pattern gösterilmiştir. Her servis için:

1. **Doc 02 §2.X'teki** ilgili servis açıklamasını oku (API endpoint'ler, sorumluluklar)
2. **Doc 07 §12.1'deki** service pattern'ı takip et
3. **Doc 07 §12.2'deki** BaseRepository'yi veri erişimi için kullan
4. Her service dosyasına `# Source: Doc 02 §2.X — {servis_adı}` yorumunu ekle

### Frontend Sayfa Oluşturma Kuralı

Doc 08'de sadece dashboard sayfası tam kod olarak verilmiştir. Diğer sayfalar için:

1. **Doc 04 §2.X'teki** ASCII wireframe'i yapısal rehber olarak kullan
2. **Doc 08 §8'deki** dashboard page yapısını şablon olarak kullan
3. **Doc 09'daki** tasarım token'ları, component varyantları ve stiller uygula
4. **Doc 08 §6'daki** hook'ları veri çekimi için kullan
5. Her sayfa dosyasına `// Source: Doc 04 §2.X — {sayfa_adı}` yorumunu ekle

### API Endpoint Oluşturma Kuralı

1. **Endpoint listesi:** Doc 02 §2.X (ilgili servis bölümü)
2. **Request/Response JSON:** Doc 03 §3.X
3. **Pydantic şemaları:** Doc 03 §4
4. **Router pattern:** Doc 07 §10.3 (auth.py örneği)
5. **Ortak response formatı:** Doc 03 §3.1 (APIResponse wrapper)

### Frontend API Fonksiyonu Oluşturma Kuralı

1. **İmza ve URL:** Doc 08 §3.2-§3.3 örneklerini takip et
2. **TypeScript tipleri:** Doc 08 §4.1-§4.4
3. **Axios client:** Doc 08 §3.1 (otomatik token, interceptor, refresh)

---

## ❌ YAPMA LİSTESİ (Anti-Patterns)

| #   | YAPMA                                 | Neden                                             |
| --- | ------------------------------------- | ------------------------------------------------- |
| 1   | `socket.io-client` bağımlılığı ekleme | Native WebSocket kullanılıyor                     |
| 2   | Ortam değişkenlerini hardcode etme    | `.env` ve `config.py` üzerinden oku               |
| 3   | Doc 07 §22'deki Dockerfile'ı kullanma | Doc 10 §2.1'deki doğru                            |
| 4   | `any` tip kullanma (TypeScript)       | Her yerde strict typing                           |
| 5   | `console.log` bırakma                 | structlog (backend), toast (frontend)             |
| 6   | Tailwind'de rastgele renk kullanma    | Token sistemi var (Doc 09 §2)                     |
| 7   | API response'u wrapper olmadan dönme  | `APIResponse` formatı kullan (Doc 03 §3.1)        |
| 8   | Test yazmadan adım tamamlama          | Her servis için en az 3 test                      |
| 9   | Doküman okumadan dosya oluşturma      | Referans haritasını kontrol et                    |
| 10  | Sıra atlamak                          | Bağımlılık zinciri var — önceki adım tamamlanmalı |

---

## 🔄 HATA KURTARMA PROSEDÜRÜ

Geliştirme sırasında hata alırsan:

### 1. Import Hatası

```
Kontrol: İlgili __init__.py dosyasında re-export var mı?
Kontrol: pyproject.toml / package.json'da bağımlılık yüklü mü?
Kontrol: Dosya yolu ve ismi dokümandaki ile aynı mı?
```

### 2. TypeScript Hata

```
Kontrol: Doc 08 §4.X'teki tip tanımı ile compare et
Kontrol: API response tipi backend schema ile uyumlu mu?
Kontrol: strict mode'da null check yapılmış mı?
```

### 3. Veritabanı/Migration Hatası

```
Kontrol: Doc 03 §2'deki tablo ile ORM model eşleşiyor mu?
Kontrol: Foreign key referansları doğru mu?
Kontrol: alembic revision --autogenerate çalıştırıldı mı?
```

### 4. Docker Hatası

```
Kontrol: Port çakışması var mı? (8000, 3000, 5432, 6379, 9092)
Kontrol: Volume mount yolları doğru mu?
Kontrol: .env dosyası docker-compose.yml ile uyumlu mu?
```

### 5. API 422 (Validation Error)

```
Kontrol: Request body Doc 03 §3.X'teki JSON ile eşleşiyor mu?
Kontrol: Pydantic schema required field'lar doğru mu?
Kontrol: Frontend gönderdiği veri backend'in beklediğiyle aynı mı?
```

---

## 📊 BAŞARI KRİTERLERİ

Proje tamamlandığında aşağıdaki kriterler sağlanmalıdır:

### Faz 0 Tamamlanma Kriterleri

- [ ] Docker compose ile tüm servisler ayağa kalkıyor
- [ ] Backend health check 200 dönüyor
- [ ] Frontend build hatasız tamamlanıyor
- [ ] Alembic migration başarılı, 16+ tablo oluşmuş
- [ ] CI pipeline (GitHub Actions) çalışıyor

### MVP (Faz 1) Tamamlanma Kriterleri

- [ ] Kullanıcı register/login yapabiliyor
- [ ] BIST hisseleri listeleniyor, arama ve filtreleme çalışıyor
- [ ] Mum grafiği gösteriliyor (TradingView)
- [ ] Endeks bazlı filtreleme çalışıyor (BIST30, BIST100, Katılım)
- [ ] Paper trading ile emir gönderilebiliyor
- [ ] Portföy ve PnL görüntülenebiliyor
- [ ] Dashboard gerçek verilerle çalışıyor
- [ ] WebSocket ile canlı fiyat güncellemesi çalışıyor
- [ ] Backend test coverage > %60
- [ ] Frontend lint + build hatasız

### Faz 2 Tamamlanma Kriterleri

- [ ] Trend analiz ekranı çalışıyor (dip + kırılım adayları)
- [ ] En az 2 strateji (MA Crossover, RSI Reversal) sinyal üretiyor
- [ ] Backtest motoru çalışıyor, 12 performans metriği hesaplanıyor
- [ ] Risk management tüm kurallarıyla aktif
- [ ] Bildirim sistemi (in-app + email) çalışıyor
- [ ] Strateji → otomatik emir akışı çalışıyor

### Faz 3 Tamamlanma Kriterleri

- [ ] En az 2 ML model production'da
- [ ] AI stratejiler backtest'te pozitif performans
- [ ] Parametre optimizasyonu (Optuna) çalışıyor
- [ ] MLflow'da experiment'lar izlenebiliyor
- [ ] Model inference < 50ms

---

_Bu doküman, bist-robogo projesinin bir AI Agent tarafından uçtan uca, sıfır hata ile geliştirilmesi için master referans dokümanıdır. Tüm geliştirme bu dokümandaki sıra, kural ve referanslara uygun şekilde yapılmalıdır._
