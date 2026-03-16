<div align="center">

# 🚀 BIST RoboGo

**AI-Powered Automated Trading Platform for Borsa Istanbul (BIST)**

[![CI](https://github.com/omerada/bist-robogo/actions/workflows/ci.yml/badge.svg)](https://github.com/omerada/bist-robogo/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 15](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6.svg)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

<p>
  <a href="#-features">Features</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-documentation">Documentation</a> •
  <a href="#-contributing">Contributing</a>
</p>

</div>

---

> An open-source, modular, AI-driven trading infrastructure for Borsa Istanbul (BIST) — featuring real-time market data, automated order execution, technical & AI-based strategies, backtesting, and a professional dashboard.

> **⚠️ Disclaimer:** This platform does **not** provide investment advice. Trading involves risk of loss. Use responsibly.

## ✨ Features

| Feature                       | Description                                                 |
| ----------------------------- | ----------------------------------------------------------- |
| **Real-Time Market Data**     | Live prices, volume, and order book via WebSocket           |
| **Automated Order Execution** | Risk-controlled buy/sell with broker adapters               |
| **Trend & Bottom Detection**  | Technical indicators (RSI, MACD, Bollinger) + AI models     |
| **Risk Management**           | Daily loss limits, position sizing, volatility controls     |
| **Backtesting Engine**        | Historical strategy simulation with detailed metrics        |
| **Professional Dashboard**    | Real-time P&L, positions, risk gauges, performance charts   |
| **Index Filtering**           | BIST30, BIST100, Participation Index support                |
| **AI Strategy Engine**        | ML-powered predictions using XGBoost, scikit-learn, PyTorch |
| **Paper Trading**             | Safe simulation mode before going live                      |
| **Notifications**             | Telegram bot & email alerts for signals and risk events     |

---

## 🏗️ Architecture

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

## 🛠️ Tech Stack

| Layer             | Technology                                        |
| ----------------- | ------------------------------------------------- |
| **Backend**       | Python 3.12+, FastAPI, Celery, SQLAlchemy 2.0     |
| **Frontend**      | Next.js 15, React 19, TypeScript 5.7, TailwindCSS |
| **Database**      | PostgreSQL 16 + TimescaleDB                       |
| **Cache / Queue** | Redis 7+, Kafka / Redpanda                        |
| **AI/ML**         | scikit-learn, XGBoost, PyTorch, TA-Lib            |
| **Monitoring**    | Prometheus, Grafana, Sentry, structlog            |
| **DevOps**        | Docker, Docker Compose, GitHub Actions            |
| **Testing**       | pytest, Vitest, Playwright                        |

---

## 📁 Project Structure

```
bist-robogo/
├── backend/                 # Python Backend (FastAPI)
│   ├── app/
│   │   ├── api/             # REST API routes (v1)
│   │   ├── brokers/         # Broker adapters (paper, live)
│   │   ├── core/            # Config, security, Redis, WebSocket
│   │   ├── indicators/      # Technical indicators (RSI, MACD, etc.)
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # Business logic layer
│   │   ├── strategies/      # Trading strategies (MA crossover, AI trend)
│   │   ├── tasks/           # Celery async tasks
│   │   └── websocket/       # Real-time WebSocket streams
│   ├── alembic/             # Database migrations
│   ├── tests/               # Backend test suite (pytest)
│   └── pyproject.toml
├── frontend/                # Next.js 15 Frontend
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   ├── components/      # React components (auth, charts, layout)
│   │   ├── hooks/           # Custom React hooks
│   │   ├── lib/             # API client, utilities
│   │   ├── stores/          # Zustand state management
│   │   └── types/           # TypeScript type definitions
│   └── package.json
├── docs/                    # Design & implementation docs (12 files)
├── docker-compose.yml       # Full dev environment (6 services)
├── Makefile                 # Common dev commands
└── .github/workflows/       # CI pipeline
```

---

## 📚 Documentation

The `docs/` directory contains 12 detailed design & implementation documents:

| #   | Document                                                                     | Topics                                                |
| --- | ---------------------------------------------------------------------------- | ----------------------------------------------------- |
| 01  | [R&D & Requirements Analysis](docs/01-ARGE-GEREKSINIM-ANALIZI.md)            | Tech research, functional/non-functional requirements |
| 02  | [System Architecture](docs/02-SISTEM-MIMARISI.md)                            | Modules, data flows, deployment                       |
| 03  | [Data Models & API](docs/03-VERI-MODELLERI-VE-API.md)                        | DB schemas, API contracts, event flows                |
| 04  | [Frontend Design & UX](docs/04-FRONTEND-TASARIM-VE-UX.md)                    | UI/UX, wireframes, component hierarchy                |
| 05  | [Development Plan & MVP](docs/05-GELISTIRME-PLANI-VE-MVP.md)                 | Sprint planning, roadmap                              |
| 06  | [Gap Analysis Report](docs/06-EKSIK-ANALIZ-RAPORU.md)                        | Coverage gaps in existing docs                        |
| 07  | [Backend Implementation Guide](docs/07-BACKEND-IMPLEMENTASYON-KILAVUZU.md)   | File structure, code patterns                         |
| 08  | [Frontend Implementation Guide](docs/08-FRONTEND-IMPLEMENTASYON-KILAVUZU.md) | Components, hooks, stores                             |
| 09  | [Design System](docs/09-TASARIM-SISTEMI.md)                                  | Color tokens, typography, component catalog           |
| 10  | [Step-by-Step Dev Guide](docs/10-ADIM-ADIM-GELISTIRME-REHBERI.md)            | Docker, CI/CD, phased tasks                           |
| 11  | [AI Agent Dev Prompt](docs/11-AI-AGENT-GELISTIRME-PROMPTU.md)                | End-to-end AI agent master prompt                     |
| 12  | [Project Status](docs/12-PROJE-DURUMU.md)                                    | Current progress & completed phases                   |

---

## 🚀 Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- [Python 3.12+](https://www.python.org/) & [Poetry](https://python-poetry.org/) (for local backend dev)
- [Node.js 20+](https://nodejs.org/) & [pnpm](https://pnpm.io/) (for local frontend dev)

### One-Command Setup (Docker)

```bash
# Clone the repository
git clone https://github.com/omerada/bist-robogo.git
cd bist-robogo

# Copy environment template
cp .env.example .env
# Edit .env with your own secrets (see .env.example for details)

# Start all services
docker compose up -d --build

# Verify
docker compose ps
# http://localhost:8000/health → 200 OK (Backend)
# http://localhost:3000         → Dashboard  (Frontend)
```

### Local Development (without Docker)

```bash
# Backend
cd backend
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (in a separate terminal)
cd frontend
pnpm install
pnpm dev
```

### Make Commands

```bash
make dev            # Start all services (Docker)
make test           # Run all tests (backend + frontend)
make backend-test   # Backend tests with coverage
make frontend-test  # Frontend unit tests
make migrate        # Run database migrations
make seed           # Seed BIST30 symbols & indexes
```

---

## 🧪 Testing

```bash
# Backend (272+ tests)
cd backend && poetry run pytest -v --cov=app

# Frontend (Vitest)
cd frontend && pnpm test

# E2E (Playwright)
cd frontend && pnpm test:e2e
```

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 🔒 Security

For security concerns, please see [SECURITY.md](SECURITY.md). Do **not** open public issues for security vulnerabilities.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## ⭐ Star History

If you find this project useful, please consider giving it a star!

---

> **⚠️ Disclaimer:** This platform does **not** provide investment advice. Trading involves risk of loss. Use responsibly. The developers are not liable for any financial losses incurred through the use of this software.
