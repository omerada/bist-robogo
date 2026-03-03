# 🚀 bist-robogo

**BIST İçin AI Destekli Otomatik Ticaret Platformu**

> Türkiye Borsası (BIST) için geliştirilmiş, yapay zeka destekli, gerçek zamanlı ve otomatik alım-satım yapabilen modüler ticaret altyapısı.

---

## 📋 Özellikler

- **Gerçek Zamanlı Veri Takibi** — Canlı piyasa fiyatları, hacim ve order book
- **Otomatik Emir Sistemi** — Risk kontrollü alım-satım
- **Trend ve Dip Tespiti** — Teknik göstergeler + AI modelleri
- **Risk Yönetimi** — Maks günlük zarar, pozisyon limitleri, volatilite kontrolü
- **Backtest Motoru** — Geçmiş veri üzerinde strateji simülasyonu
- **Profesyonel Dashboard** — Canlı fiyat, PnL, risk, performans
- **Endeks Seçimi** — BIST30, BIST100, Katılım Endeksi filtreleme
- **Trend Analiz Ekranı** — Günlük/haftalık/aylık trend dip ve kırılım analizi

---

## 🏗️ Mimari

```
                    Frontend (Next.js 15)
                           │
                    API Gateway (Nginx)
                           │
                    Backend (FastAPI)
                    ┌──────┼──────┐
                    │      │      │
               Market   Trading  Strategy
               Data     Engine   Engine
                    │      │      │
              ┌─────┼──────┼──────┼─────┐
              │     │      │      │     │
          PostgreSQL TimescaleDB Redis Kafka MinIO
```

## 🛠️ Teknoloji Stack

| Katman         | Teknoloji                                     |
| -------------- | --------------------------------------------- |
| **Backend**    | Python 3.12+, FastAPI, Celery, SQLAlchemy     |
| **Frontend**   | Next.js 15, React 19, TypeScript, TailwindCSS |
| **Veritabanı** | PostgreSQL 16, TimescaleDB                    |
| **Cache**      | Redis 7+                                      |
| **Mesajlaşma** | Kafka / Redpanda                              |
| **AI/ML**      | scikit-learn, XGBoost, PyTorch, TA-Lib        |
| **Monitoring** | Prometheus, Grafana, Loki, Sentry             |
| **DevOps**     | Docker, GitHub Actions, Terraform             |

---

## 📁 Proje Yapısı

```
bist-robogo/
├── docs/                               # Proje dökümanları (11 adet)
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
├── backend/                            # Python Backend (FastAPI)
│   ├── app/
│   │   ├── api/                        # API route'ları
│   │   │   ├── router.py
│   │   │   ├── health.py
│   │   │   └── v1/
│   │   │       ├── auth.py
│   │   │       ├── market.py
│   │   │       ├── orders.py
│   │   │       ├── portfolio.py
│   │   │       ├── strategies.py
│   │   │       ├── backtest.py
│   │   │       ├── risk.py
│   │   │       └── analysis.py
│   │   ├── core/                       # Çekirdek yapılandırma
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── database.py
│   │   │   └── redis_client.py
│   │   ├── models/                     # SQLAlchemy modelleri
│   │   ├── schemas/                    # Pydantic şemaları
│   │   ├── services/                   # İş mantığı
│   │   │   ├── auth_service.py
│   │   │   ├── market_data_service.py
│   │   │   ├── trading_service.py
│   │   │   ├── risk_service.py
│   │   │   ├── strategy_service.py
│   │   │   ├── backtest_service.py
│   │   │   ├── portfolio_service.py
│   │   │   ├── ai_ml_service.py
│   │   │   └── notification_service.py
│   │   ├── repositories/              # Repository pattern
│   │   ├── strategies/                 # Trading stratejileri
│   │   │   ├── base.py
│   │   │   ├── ma_crossover.py
│   │   │   ├── rsi_reversal.py
│   │   │   └── ai_trend.py
│   │   ├── indicators/                 # Teknik gösterge hesaplamaları
│   │   │   └── momentum.py
│   │   ├── brokers/                    # Broker adaptörleri
│   │   │   ├── base.py
│   │   │   └── paper_broker.py
│   │   ├── ml/                         # Makine öğrenmesi
│   │   │   ├── features.py
│   │   │   ├── models/
│   │   │   ├── training.py
│   │   │   └── serving.py
│   │   ├── tasks/                      # Celery görevleri
│   │   │   ├── celery_app.py
│   │   │   └── market_tasks.py
│   │   ├── websocket/                  # WebSocket yönetimi
│   │   │   └── market_stream.py
│   │   ├── utils/                      # Yardımcı fonksiyonlar
│   │   └── main.py                     # FastAPI app (create_app factory)
│   ├── alembic/                        # Alembic migrasyonları
│   ├── scripts/                        # Yardımcı scriptler
│   │   └── seed_symbols.py
│   ├── tests/                          # Testler
│   ├── pyproject.toml
│   └── Dockerfile
│
├── frontend/                           # Next.js Frontend
│   ├── src/
│   │   ├── app/                        # Next.js App Router
│   │   │   ├── layout.tsx
│   │   │   ├── globals.css
│   │   │   ├── (auth)/                 # Auth sayfaları
│   │   │   └── (dashboard)/            # Dashboard sayfaları
│   │   ├── components/                 # React bileşenleri
│   │   │   ├── auth/
│   │   │   ├── charts/
│   │   │   ├── layout/
│   │   │   ├── providers/
│   │   │   └── shared/
│   │   ├── hooks/                      # Custom hooks
│   │   ├── lib/                        # API client ve yardımcılar
│   │   │   ├── api/
│   │   │   └── utils/
│   │   ├── stores/                     # Zustand stores
│   │   └── types/                      # TypeScript tipleri
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml                  # Tüm servisler (dev ortam)
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── .env.example
├── .gitignore
├── README.md
└── Makefile
```

---

## 📚 Dokümantasyon

### Ar-Ge ve Tasarım Dokümanları

| Doküman                                                                | Açıklama                                           |
| ---------------------------------------------------------------------- | -------------------------------------------------- |
| [01 — Ar-Ge ve Gereksinim Analizi](docs/01-ARGE-GEREKSINIM-ANALIZI.md) | Teknoloji araştırması, gereksinimler, risk analizi |
| [02 — Sistem Mimarisi](docs/02-SISTEM-MIMARISI.md)                     | Modüller, veri akışları, deployment                |
| [03 — Veri Modelleri ve API](docs/03-VERI-MODELLERI-VE-API.md)         | DB şemaları, API sözleşmeleri, event flow          |
| [04 — Frontend Tasarım](docs/04-FRONTEND-TASARIM-VE-UX.md)             | UI/UX, ekran planları, component mimari            |
| [05 — Geliştirme Planı](docs/05-GELISTIRME-PLANI-VE-MVP.md)            | MVP, sprintler, yol haritası                       |

### Implementasyon ve Geliştirme Dokümanları

| Doküman                                                                              | Açıklama                                          |
| ------------------------------------------------------------------------------------ | ------------------------------------------------- |
| [06 — Eksik Analiz Raporu](docs/06-EKSIK-ANALIZ-RAPORU.md)                           | Mevcut dokümanların gap analizi                   |
| [07 — Backend Implementasyon Kılavuzu](docs/07-BACKEND-IMPLEMENTASYON-KILAVUZU.md)   | Backend dosya yapısı, kod şablonları, pattern'ler |
| [08 — Frontend Implementasyon Kılavuzu](docs/08-FRONTEND-IMPLEMENTASYON-KILAVUZU.md) | Frontend bileşenler, hook'lar, store'lar          |
| [09 — Tasarım Sistemi](docs/09-TASARIM-SISTEMI.md)                                   | Renk token'ları, tipografi, component catalog     |
| [10 — Adım Adım Geliştirme Rehberi](docs/10-ADIM-ADIM-GELISTIRME-REHBERI.md)         | Docker, CI/CD, faz bazlı görev sırası             |

### Geliştirme Prompt Dokümanı

| Doküman                                                                    | Açıklama                                         |
| -------------------------------------------------------------------------- | ------------------------------------------------ |
| [11 — AI Agent Geliştirme Promptu](docs/11-AI-AGENT-GELISTIRME-PROMPTU.md) | Uçtan uca geliştirme için AI Agent master prompt |

---

## 🚀 Hızlı Başlangıç

```bash
# Repository'yi klonla
git clone https://github.com/your-username/bist-robogo.git
cd bist-robogo

# Ortam değişkenlerini ayarla
cp .env.example .env
# .env dosyasını düzenle

# Docker ile tüm servisleri başlat
docker compose up -d --build

# Servis durumlarını kontrol et
docker compose ps

# Backend (geliştirme — Docker dışında çalıştırmak için)
cd backend
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (geliştirme — Docker dışında çalıştırmak için)
cd frontend
pnpm install
pnpm dev

# Doğrulama
# http://localhost:8000/health → 200 OK
# http://localhost:3000 → Next.js sayfası
```

---

## 📄 Lisans

Bu proje özel kullanım içindir. Tüm hakları saklıdır.

---

> **⚠️ Uyarı:** Bu platform yatırım tavsiyesi vermemektedir. Ticaret işlemleri kayıp riski taşır. Sorumlu kullanım esastır.
