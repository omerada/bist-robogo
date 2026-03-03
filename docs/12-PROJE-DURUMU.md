# bist-robogo — Proje Durumu

> **Son Güncelleme:** Faz 1 Sprint 1.3 tamamlandı — 45/45 test geçiyor  
> **Aktif Faz:** Faz 1 — MVP Temel Özellikler  
> **Aktif Sprint:** Sprint 1.3 tamamlandı, Faz 2'ye geçiş hazır

---

## Genel Durum Özeti

| Faz | Ad                       | Durum         | İlerleme   |
| --- | ------------------------ | ------------- | ---------- |
| 0   | Altyapı Kurulumu         | ✅ Tamamlandı | 6/6 adım   |
| 1   | MVP Temel Özellikler     | ✅ Tamamlandı | 3/3 sprint |
| 2   | Genişletme               | ⏳ Bekliyor   | —          |
| 3   | AI/ML Entegrasyonu       | ⏳ Bekliyor   | —          |
| 4   | Ölçekleme ve Prodüksiyon | ⏳ Bekliyor   | —          |

---

## Test Durumu — 45/45 ✅

| Test Dosyası      | Test Sayısı | Durum     |
| ----------------- | ----------- | --------- |
| `test_auth.py`    | 10          | ✅        |
| `test_health.py`  | 2           | ✅        |
| `test_market.py`  | 13          | ✅        |
| `test_trading.py` | 20          | ✅        |
| **Toplam**        | **45**      | **5.55s** |

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

---

## Build Durumu

| Bileşen            | Durum | Detay                         |
| ------------------ | ----- | ----------------------------- |
| Backend (Docker)   | ✅    | FastAPI + Uvicorn, healthy    |
| Frontend (Next.js) | ✅    | 13 sayfa, 0 TypeScript hatası |
| PostgreSQL 16      | ✅    | 20 tablo + TimescaleDB        |
| Redis 7            | ✅    | Cache + Celery broker         |
| pytest             | ✅    | 45/45, 5.55s, %58 coverage    |

---

## Mevcut Dosya Envanteri

### Backend (~70+ kaynak dosya)

- **Modeller (11):** user, market, order, portfolio, strategy, backtest, risk, broker, notification, audit, base
- **Şemalar (10):** common, auth, market, order, portfolio, strategy, backtest, risk, analysis
- **API v1 (9):** auth, market, orders, portfolio, strategies, backtest, risk, trends, notifications
- **Core (4):** security, redis_client, rate_limiter, websocket_manager
- **Servisler (4):** auth_service, market_data_service, trading_service, portfolio_service
- **Repositories (4):** user_repository, market_repository, order_repository, portfolio_repository
- **Altyapı:** celery_app, market_tasks, brokers (3), indicators/momentum, strategies/base, websocket/market_stream
- **Testler (4):** test_auth (10), test_health (2), test_market (13), test_trading (20)

### Frontend (~50+ src/ dosya)

- **Sayfalar (11):** login, register, dashboard, market, market/[symbol], trends, strategies, backtest, portfolio, orders, settings
- **Dashboard \_components (6):** dashboard-stats, equity-curve, allocation-chart, recent-orders, recent-signals, risk-status
- **Market components (6):** symbol-table, symbol-card, quote-ticker, loading-skeleton, order-form
- **Portfolio components (1):** position-card
- **Bileşenler (7+):** stat-card, candlestick-chart, auth-guard, sidebar, header, theme-provider, query-provider
- **Hooks (5):** use-websocket, use-market-data, use-portfolio, use-trading
- **Stores (3):** auth-store, market-store, ui-store
- **API lib (4):** client, market, orders, trading
- **Types (4):** market, order, portfolio, strategy

---

_Bu doküman, projenin mevcut durumunu takip etmek için düzenli olarak güncellenecektir._
