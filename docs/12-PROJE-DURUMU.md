# bist-robogo — Proje Durumu

> **Son Güncelleme:** Faz 2 Sprint 2.1 tamamlandı — backend 70/70 test, frontend build OK  
> **Aktif Faz:** Faz 2 — Genişletme  
> **Aktif Sprint:** Sprint 2.2 — Backtest Motoru (sırada)

---

## Genel Durum Özeti

| Faz | Ad                       | Durum           | İlerleme   |
| --- | ------------------------ | --------------- | ---------- |
| 0   | Altyapı Kurulumu         | ✅ Tamamlandı   | 6/6 adım   |
| 1   | MVP Temel Özellikler     | ✅ Tamamlandı   | 3/3 sprint |
| 2   | Genişletme               | 🔄 Devam Ediyor | 1/3 sprint |
| 3   | AI/ML Entegrasyonu       | ⏳ Bekliyor     | —          |
| 4   | Ölçekleme ve Prodüksiyon | ⏳ Bekliyor     | —          |

---

## Test Durumu — 70/70 ✅

| Test Dosyası         | Test Sayısı | Durum     |
| -------------------- | ----------- | --------- |
| `test_auth.py`       | 10          | ✅        |
| `test_health.py`     | 2           | ✅        |
| `test_market.py`     | 13          | ✅        |
| `test_trading.py`    | 20          | ✅        |
| `test_trends.py`     | 10          | ✅        |
| `test_strategies.py` | 15          | ✅        |
| **Toplam**           | **70**      | **7.54s** |

---

## Faz 0 — Altyapı Kurulumu ✅

### Tamamlanan Adımlar

| Adım | Açıklama                                       | Durum |
| ---- | ---------------------------------------------- | ----- |
| 0.1  | Proje kök yapısı (docker-compose, init-db, CI) | ✅    |
| 0.2  | Backend projesi (50+ dosya, 12 modül)          | ✅    |
| 0.3  | Alembic migration (20 tablo)                   | ✅    |
| 0.4  | Backend çalıştırma + health check              | ✅    |
| 0.5  | Frontend projesi (38+ dosya)                   | ✅    |
| 0.6  | Docker Compose entegrasyonu (6 servis)         | ✅    |

### İmplementasyon Sırasında Uygulanan Düzeltmeler

| #   | Düzeltme                                                                 | Etkilenen Dosya(lar)                          |
| --- | ------------------------------------------------------------------------ | --------------------------------------------- |
| 1   | `passlib` → doğrudan `bcrypt` modülü (passlib + bcrypt 4.2+ uyumsuzluğu) | `core/security.py`                            |
| 2   | `CORS_ORIGINS` JSON format + `field_validator`                           | `config.py`                                   |
| 3   | `ACCESS_TOKEN_EXPIRE_MINUTES` → `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`        | `services/auth_service.py`                    |
| 4   | `docker-compose.yml`: `version: "3.9"` kaldırıldı                        | `docker-compose.yml`                          |
| 5   | `backend_venv:/app/.venv` volume eklendi                                 | `docker-compose.yml`                          |
| 6   | `backend/.dockerignore` oluşturuldu                                      | `backend/.dockerignore`                       |
| 7   | `api/v1/analysis.py` → `api/v1/trends.py` olarak adlandırıldı            | `api/v1/trends.py`, `api/router.py`           |
| 8   | TailwindCSS v4 → v3.4.17 downgrade (shadcn/ui uyumluluğu)                | `frontend/package.json`, `tailwind.config.ts` |
| 9   | `autoprefixer` + `tailwindcss-animate` eklendi                           | `frontend/postcss.config.mjs`                 |
| 10  | Next.js 15 async params fix (Promise params)                             | Tüm `[slug]` sayfalar                         |
| 11  | `BaseHTTPMiddleware` → pure ASGI middleware                              | `middleware.py`                               |
| 12  | pytest event loop scope fix (`loop_scope="session"`)                     | `conftest.py`, tüm test dosyaları             |
| 13  | `APIResponse.meta` tip genişletme (`PaginationMeta \| dict \| None`)     | `schemas/common.py`                           |
| 14  | OHLCVRepository try/except (hypertable yoksa graceful degrade)           | `repositories/market_repository.py`           |
| 15  | PaperBroker fallback simulation pricing (Redis yoksa hashlib-based)      | `brokers/paper_broker.py`                     |
| 16  | Decimal/float tip uyumsuzluğu fix (SQLAlchemy Numeric)                   | `services/trading_service.py`                 |
| 17  | İdempotent test_user fixture (commit sonrası duplicate önleme)           | `tests/conftest.py`                           |
| 18  | Frontend `.dockerignore` oluşturuldu (821MB context → 7KB)               | `frontend/.dockerignore`                      |
| 19  | Dockerfile multi-stage `target: dev` + `output: standalone`              | `frontend/Dockerfile`, `next.config.ts`       |
| 20  | `docker-compose.yml`: `TEST_DATABASE_URL` + frontend volume kaldırma     | `docker-compose.yml`                          |

---

## Faz 1 — MVP Temel Özellikler ✅

### Sprint 1.1 — Auth + Dashboard ✅

| #      | Görev                                 | Durum | Not                                                           |
| ------ | ------------------------------------- | ----- | ------------------------------------------------------------- |
| 1.1.1  | Auth service impl.                    | ✅    | `services/auth_service.py` — register, login, refresh, logout |
| 1.1.2  | User repository                       | ✅    | `repositories/user_repository.py`                             |
| 1.1.3  | Auth API (register/login/me/logout)   | ✅    | `api/v1/auth.py` — 10 test                                    |
| 1.1.4  | Login sayfası (react-hook-form + zod) | ✅    | `app/(auth)/login/page.tsx`                                   |
| 1.1.5  | Register sayfası (tam form)           | ✅    | `app/(auth)/register/page.tsx`                                |
| 1.1.6  | Dashboard layout                      | ✅    | sidebar + header                                              |
| 1.1.7  | Dashboard stat kartları               | ✅    | Mock data                                                     |
| 1.1.8  | Auth guard                            | ✅    | `components/auth/auth-guard.tsx`                              |
| 1.1.9  | Seed data                             | ✅    | 30 sembol + 5 endeks + 86 index_component ilişkisi            |
| 1.1.10 | Backend testleri                      | ✅    | `test_auth.py` (10), `test_health.py` (2)                     |
| 1.1.11 | 24 shadcn/ui bileşeni                 | ✅    | button, card, input, dialog, toast, vb.                       |

### Sprint 1.2 — Piyasa Verisi + Grafik ✅

| #     | Görev                                    | Durum | Not                                                       |
| ----- | ---------------------------------------- | ----- | --------------------------------------------------------- |
| 1.2.1 | Market repository (Symbol, Index, OHLCV) | ✅    | `repositories/market_repository.py`                       |
| 1.2.2 | Market data service                      | ✅    | `services/market_data_service.py`                         |
| 1.2.3 | Market API (6 endpoint)                  | ✅    | symbols list/detail/quote/history, indices, sectors       |
| 1.2.4 | Market şemaları                          | ✅    | `schemas/market.py` — 10 şema                             |
| 1.2.5 | İndikatör hesaplama                      | ✅    | `indicators/momentum.py` — RSI, MACD, SMA, EMA, Bollinger |
| 1.2.6 | Frontend market sayfası                  | ✅    | symbol-table, symbol-card, quote-ticker, loading-skeleton |
| 1.2.7 | Sembol detay + grafik sayfası            | ✅    | `market/[symbol]/page.tsx` + lightweight-charts           |
| 1.2.8 | Frontend hooks + store                   | ✅    | `use-market-data.ts`, `market-store.ts`                   |
| 1.2.9 | Market testleri                          | ✅    | `test_market.py` — 13 test                                |

### Sprint 1.3 — Paper Trading + Portföy ✅

| #      | Görev                           | Durum | Not                                                                               |
| ------ | ------------------------------- | ----- | --------------------------------------------------------------------------------- |
| 1.3.1  | Order repository                | ✅    | `repositories/order_repository.py` — OrderRepo + TradeRepo                        |
| 1.3.2  | Portfolio repository            | ✅    | `repositories/portfolio_repository.py` — Position, Portfolio, Snapshot            |
| 1.3.3  | Trading service                 | ✅    | `services/trading_service.py` — order CRUD, validation, position/portfolio update |
| 1.3.4  | Portfolio service               | ✅    | `services/portfolio_service.py` — summary, positions, history                     |
| 1.3.5  | Orders API (4 endpoint)         | ✅    | GET list, POST create, GET detail, DELETE cancel                                  |
| 1.3.6  | Portfolio API (3 endpoint)      | ✅    | GET summary, GET positions, GET history                                           |
| 1.3.7  | Paper broker (fallback pricing) | ✅    | `brokers/paper_broker.py` — hashlib-based simulation                              |
| 1.3.8  | Frontend trading API client     | ✅    | `lib/api/trading.ts`                                                              |
| 1.3.9  | Frontend trading hooks          | ✅    | `hooks/use-trading.ts` — 6 hook + 2 mutation                                      |
| 1.3.10 | Order form bileşeni             | ✅    | `components/market/order-form.tsx` — buy/sell, limit/market                       |
| 1.3.11 | Position card bileşeni          | ✅    | `components/portfolio/position-card.tsx`                                          |
| 1.3.12 | Portfolio sayfası               | ✅    | 7 summary card + pozisyon grid + boş durum                                        |
| 1.3.13 | Orders sayfası                  | ✅    | Filtreli tablo + durumlar + iptal + OrderForm sidebar                             |
| 1.3.14 | Trading testleri                | ✅    | `test_trading.py` — 20 test                                                       |

---

## Faz 2 — Genişletme 🔄

### Sprint 2.1 — Trend Analiz + Strateji ✅

| #      | Görev                                      | Durum | Not                                                                      |
| ------ | ------------------------------------------ | ----- | ------------------------------------------------------------------------ |
| 2.1.1  | Trend indikatörleri (ADX, OBV, S/R)        | ✅    | `indicators/trend.py` — 9 fonksiyon                                      |
| 2.1.2  | Strategy repository + Signal repository    | ✅    | `repositories/strategy_repository.py`                                    |
| 2.1.3  | Trend analysis service                     | ✅    | `services/trend_analysis_service.py` — dip + breakout scoring            |
| 2.1.4  | Strategy service (CRUD + activate)         | ✅    | `services/strategy_service.py` — 9 metod                                 |
| 2.1.5  | Trend API (2 endpoint)                     | ✅    | `api/v1/trends.py` — GET trends, GET sectors                             |
| 2.1.6  | Strategy API (8 endpoint)                  | ✅    | `api/v1/strategies.py` — CRUD + activate + signals + performance         |
| 2.1.7  | MA Crossover strateji impl.                | ✅    | `strategies/ma_crossover.py` — Golden/Death Cross + ADX+RSI konfirmasyon |
| 2.1.8  | RSI Reversal strateji impl.                | ✅    | `strategies/rsi_reversal.py` — Stochastic+Bollinger+Volume konfirmasyon  |
| 2.1.9  | Trend analysis frontend (API+hooks+sayfa)  | ✅    | analysis.ts, use-trends.ts, dip-candidate-card, breakout-candidate-card  |
| 2.1.10 | Strategy frontend (API+hooks+sayfa)        | ✅    | strategies.ts, use-strategies.ts, strategy-card, create-strategy-dialog  |
| 2.1.11 | Trend + Strategy testleri                  | ✅    | `test_trends.py` (10), `test_strategies.py` (15)                         |
| 2.1.12 | Docker frontend .dockerignore + dev target | ✅    | .dockerignore, Dockerfile target dev, next.config standalone             |

---

## Doğrulanmış API Akışları

| Akış                       | Durum | Detay                                               |
| -------------------------- | ----- | --------------------------------------------------- |
| Auth Register/Login/Me     | ✅    | JWT token, password hash, role-based                |
| Health + Ready             | ✅    | DB + Redis kontrol                                  |
| Symbol CRUD + Index filter | ✅    | 30 sembol, 5 endeks, sector filter                  |
| Quote + OHLCV History      | ✅    | Graceful degrade (hypertable yoksa)                 |
| Portfolio Summary          | ✅    | ₺100K başlangıç, auto-create                        |
| Create Buy Order           | ✅    | Market/Limit, paper broker fill, Decimal arithmetic |
| Position Tracking          | ✅    | Ortalama maliyet, kısmi satış, PnL hesaplama        |
| Create Sell Order          | ✅    | Pozisyon kontrol, realize PnL                       |
| Cancel Order               | ✅    | Sadece bekleyen emirler                             |
| Portfolio Update           | ✅    | Nakit, yatırım, toplam değer güncelleme             |
| Trend Analysis             | ✅    | Dip/Breakout scoring, period/index/type filters     |
| Strategy CRUD              | ✅    | Create, update, delete, activate, deactivate        |
| Strategy Signals           | ✅    | Signal list, performance metrics                    |

---

## Build Durumu

| Bileşen            | Durum | Detay                         |
| ------------------ | ----- | ----------------------------- |
| Backend (Docker)   | ✅    | FastAPI + Uvicorn, healthy    |
| Frontend (Next.js) | ✅    | 13 sayfa, 0 TypeScript hatası |
| PostgreSQL 16      | ✅    | 20 tablo + TimescaleDB        |
| Redis 7            | ✅    | Cache + Celery broker         |
| pytest             | ✅    | 70/70, 7.54s, %58 coverage    |

---

## Mevcut Dosya Envanteri

### Backend (~70+ kaynak dosya)

- **Modeller (11):** user, market, order, portfolio, strategy, backtest, risk, broker, notification, audit, base
- **Şemalar (10):** common, auth, market, order, portfolio, strategy, backtest, risk, analysis
- **API v1 (9):** auth, market, orders, portfolio, strategies, backtest, risk, trends, notifications
- **Core (4):** security, redis_client, rate_limiter, websocket_manager
- **Servisler (6):** auth_service, market_data_service, trading_service, portfolio_service, trend_analysis_service, strategy_service
- **Repositories (5):** user_repository, market_repository, order_repository, portfolio_repository, strategy_repository
- **İndikatörler (2):** indicators/momentum, indicators/trend (ADX, OBV, S/R, MACD crossover)
- **Stratejiler (3):** strategies/base, strategies/ma_crossover, strategies/rsi_reversal
- **Altyapı:** celery_app, market_tasks, brokers (3), websocket/market_stream
- **Testler (6):** test_auth (10), test_health (2), test_market (13), test_trading (20), test_trends (10), test_strategies (15)

### Frontend (~50+ src/ dosya)

- **Sayfalar (11):** login, register, dashboard, market, market/[symbol], trends, strategies, backtest, portfolio, orders, settings
- **Dashboard \_components (6):** dashboard-stats, equity-curve, allocation-chart, recent-orders, recent-signals, risk-status
- **Market components (6):** symbol-table, symbol-card, quote-ticker, loading-skeleton, order-form
- **Portfolio components (1):** position-card
- **Bileşenler (7+):** stat-card, candlestick-chart, auth-guard, sidebar, header, theme-provider, query-provider
- **Trend components (2):** dip-candidate-card, breakout-candidate-card
- **Strategy components (2):** strategy-card, create-strategy-dialog
- **Hooks (7):** use-websocket, use-market-data, use-portfolio, use-trading, use-trends, use-strategies
- **Stores (3):** auth-store, market-store, ui-store
- **API lib (6):** client, market, orders, trading, analysis, strategies
- **Types (4):** market, order, portfolio, strategy

---

_Bu doküman, projenin mevcut durumunu takip etmek için düzenli olarak güncellenecektir._
