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
├── docs/                           # Proje dökümanları
│   ├── 01-ARGE-GEREKSINIM-ANALIZI.md
│   ├── 02-SISTEM-MIMARISI.md
│   ├── 03-VERI-MODELLERI-VE-API.md
│   ├── 04-FRONTEND-TASARIM-VE-UX.md
│   └── 05-GELISTIRME-PLANI-VE-MVP.md
│
├── backend/                        # Python Backend (FastAPI)
│   ├── app/
│   │   ├── api/                    # API route'ları
│   │   │   └── v1/
│   │   │       ├── auth.py
│   │   │       ├── market.py
│   │   │       ├── orders.py
│   │   │       ├── portfolio.py
│   │   │       ├── strategies.py
│   │   │       ├── backtest.py
│   │   │       ├── risk.py
│   │   │       └── analysis.py
│   │   ├── core/                   # Çekirdek yapılandırma
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── database.py
│   │   ├── models/                 # SQLAlchemy modelleri
│   │   ├── schemas/                # Pydantic şemaları
│   │   ├── services/               # İş mantığı
│   │   │   ├── market_data.py
│   │   │   ├── trading_engine.py
│   │   │   ├── risk_manager.py
│   │   │   ├── strategy_engine.py
│   │   │   ├── backtest_engine.py
│   │   │   ├── portfolio.py
│   │   │   └── notification.py
│   │   ├── strategies/             # Trading stratejileri
│   │   │   ├── base.py
│   │   │   ├── ma_crossover.py
│   │   │   ├── rsi_reversal.py
│   │   │   └── ai_trend.py
│   │   ├── ml/                     # Makine öğrenmesi
│   │   │   ├── features.py
│   │   │   ├── models/
│   │   │   ├── training.py
│   │   │   └── serving.py
│   │   ├── adapters/               # Dış servis adaptörleri
│   │   │   ├── broker_base.py
│   │   │   ├── is_yatirim.py
│   │   │   └── yahoo_finance.py
│   │   ├── workers/                # Celery worker'ları
│   │   └── main.py                 # FastAPI app
│   ├── migrations/                 # Alembic migrasyonları
│   ├── tests/                      # Testler
│   ├── pyproject.toml
│   └── Dockerfile
│
├── frontend/                       # Next.js Frontend
│   ├── src/
│   │   ├── app/                    # Next.js App Router
│   │   ├── components/             # React bileşenleri
│   │   ├── hooks/                  # Custom hooks
│   │   ├── lib/                    # Yardımcı kütüphaneler
│   │   ├── stores/                 # Zustand stores
│   │   └── types/                  # TypeScript tipleri
│   ├── package.json
│   └── Dockerfile
│
├── infra/                          # Altyapı yapılandırmaları
│   ├── docker/
│   │   ├── docker-compose.yml
│   │   ├── docker-compose.dev.yml
│   │   └── docker-compose.prod.yml
│   ├── nginx/
│   ├── prometheus/
│   ├── grafana/
│   └── terraform/
│
├── scripts/                        # Yardımcı scriptler
│   ├── seed_data.py
│   ├── fetch_historical.py
│   └── run_backtest.py
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
│
├── .env.example
├── .gitignore
├── README.md
└── Makefile
```

---

## 📚 Dokümantasyon

| Doküman                                                                | Açıklama                                           |
| ---------------------------------------------------------------------- | -------------------------------------------------- |
| [01 — Ar-Ge ve Gereksinim Analizi](docs/01-ARGE-GEREKSINIM-ANALIZI.md) | Teknoloji araştırması, gereksinimler, risk analizi |
| [02 — Sistem Mimarisi](docs/02-SISTEM-MIMARISI.md)                     | Modüller, veri akışları, deployment                |
| [03 — Veri Modelleri ve API](docs/03-VERI-MODELLERI-VE-API.md)         | DB şemaları, API sözleşmeleri, event flow          |
| [04 — Frontend Tasarım](docs/04-FRONTEND-TASARIM-VE-UX.md)             | UI/UX, ekran planları, component mimari            |
| [05 — Geliştirme Planı](docs/05-GELISTIRME-PLANI-VE-MVP.md)            | MVP, sprintler, yol haritası                       |

---

## 🚀 Hızlı Başlangıç

```bash
# Repository'yi klonla
git clone https://github.com/your-username/bist-robogo.git
cd bist-robogo

# Docker ile tüm servisleri başlat
docker-compose -f infra/docker/docker-compose.dev.yml up -d

# Backend (geliştirme)
cd backend
poetry install
poetry run uvicorn app.main:app --reload --port 8000

# Frontend (geliştirme)
cd frontend
pnpm install
pnpm dev
```

---

## 📄 Lisans

Bu proje özel kullanım içindir. Tüm hakları saklıdır.

---

> **⚠️ Uyarı:** Bu platform yatırım tavsiyesi vermemektedir. Ticaret işlemleri kayıp riski taşır. Sorumlu kullanım esastır.
