# bist-robogo — Adım Adım Geliştirme Rehberi

> **Proje:** bist-robogo — BIST İçin AI Destekli Otomatik Ticaret Platformu  
> **Versiyon:** 1.0  
> **Tarih:** 2026-03-03  
> **Amaç:** AI Agent'ın projeyi komut komut, dosya dosya, sıfır hata ile geliştirmesi.

---

## 1. Docker Compose (Geliştirme Ortamı)

### 1.1 docker-compose.yml

Proje kök dizininde oluşturulacak.

```yaml
version: "3.9"

services:
  # ── PostgreSQL 16 + TimescaleDB ──
  postgres:
    image: timescale/timescaledb:latest-pg16
    container_name: bist-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: bist_user
      POSTGRES_PASSWORD: bist_dev_pass_2026
      POSTGRES_DB: bist_robogo
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/01-init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U bist_user -d bist_robogo"]
      interval: 5s
      timeout: 5s
      retries: 5

  # ── Redis 7 ──
  redis:
    image: redis:7-alpine
    container_name: bist-redis
    restart: unless-stopped
    command: redis-server --requirepass bist_redis_pass_2026 --maxmemory 256mb --maxmemory-policy allkeys-lru
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "bist_redis_pass_2026", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  # ── Backend (FastAPI) ──
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: bist-backend
    restart: unless-stopped
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    environment:
      - APP_ENV=development
      - DEBUG=true
      - DATABASE_URL=postgresql+asyncpg://bist_user:bist_dev_pass_2026@postgres:5432/bist_robogo
      - REDIS_URL=redis://:bist_redis_pass_2026@redis:6379/0
      - JWT_SECRET_KEY=dev-jwt-secret-key-change-in-production-2026
      - JWT_ALGORITHM=HS256
      - ACCESS_TOKEN_EXPIRE_MINUTES=30
      - REFRESH_TOKEN_EXPIRE_DAYS=30
      - CORS_ORIGINS=http://localhost:3000
      - LOG_LEVEL=DEBUG
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  # ── Celery Worker ──
  celery-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: bist-celery-worker
    restart: unless-stopped
    command: celery -A app.tasks.celery_app worker --loglevel=info --concurrency=4
    environment:
      - APP_ENV=development
      - DATABASE_URL=postgresql+asyncpg://bist_user:bist_dev_pass_2026@postgres:5432/bist_robogo
      - REDIS_URL=redis://:bist_redis_pass_2026@redis:6379/0
      - CELERY_BROKER_URL=redis://:bist_redis_pass_2026@redis:6379/1
      - CELERY_RESULT_BACKEND=redis://:bist_redis_pass_2026@redis:6379/2
    volumes:
      - ./backend:/app
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  # ── Celery Beat (Scheduler) ──
  celery-beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: bist-celery-beat
    restart: unless-stopped
    command: celery -A app.tasks.celery_app beat --loglevel=info
    environment:
      - APP_ENV=development
      - DATABASE_URL=postgresql+asyncpg://bist_user:bist_dev_pass_2026@postgres:5432/bist_robogo
      - REDIS_URL=redis://:bist_redis_pass_2026@redis:6379/0
      - CELERY_BROKER_URL=redis://:bist_redis_pass_2026@redis:6379/1
      - CELERY_RESULT_BACKEND=redis://:bist_redis_pass_2026@redis:6379/2
    volumes:
      - ./backend:/app
    depends_on:
      redis:
        condition: service_healthy

  # ── Frontend (Next.js) ──
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: bist-frontend
    restart: unless-stopped
    command: pnpm dev
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NEXT_PUBLIC_WS_URL=ws://localhost:8000
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:
```

### 1.2 scripts/init-db.sql

```sql
-- TimescaleDB extension'ı etkinleştir
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Bilgi mesajı
DO $$
BEGIN
  RAISE NOTICE 'bist_robogo veritabanı başarıyla hazırlandı.';
END $$;
```

---

## 2. Backend Dockerfile

### 2.1 backend/Dockerfile

```dockerfile
# ── Stage 1: Builder ──
FROM python:3.12-slim AS builder

WORKDIR /app

# Sistem bağımlılıkları
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Poetry kur
ENV POETRY_VERSION=1.8.4
RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

# Bağımlılıkları kopyala ve kur
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.in-project true && \
    poetry install --no-interaction --no-ansi --no-root

# ── Stage 2: Runtime ──
FROM python:3.12-slim AS runtime

WORKDIR /app

# Runtime sistem bağımlılıkları
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 curl && \
    rm -rf /var/lib/apt/lists/*

# Virtual env'i kopyala
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Uygulama kodunu kopyala
COPY . .

# Non-root kullanıcı
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 3. Frontend Dockerfile

### 3.1 frontend/Dockerfile

```dockerfile
FROM node:20-alpine AS base
RUN corepack enable

# ── Dependencies ──
FROM base AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# ── Builder ──
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN pnpm build

# ── Runner ──
FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

---

## 4. GitHub Actions CI/CD

### 4.1 .github/workflows/ci.yml

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: "3.12"
  NODE_VERSION: "20"
  PNPM_VERSION: "9"

jobs:
  # ── Backend Tests ──
  backend-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: timescale/timescaledb:latest-pg16
        env:
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd="pg_isready -U test_user -d test_db"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=5

      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd="redis-cli ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=5

    defaults:
      run:
        working-directory: backend

    steps:
      - uses: actions/checkout@v4

      - name: Python kurulumu
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Poetry kurulumu
        uses: snok/install-poetry@v1
        with:
          version: 1.8.4
          virtualenvs-create: true
          virtualenvs-in-project: true

      - name: Bağımlılık cache
        uses: actions/cache@v4
        with:
          path: backend/.venv
          key: venv-${{ runner.os }}-${{ hashFiles('backend/poetry.lock') }}

      - name: Bağımlılıkları kur
        run: poetry install --no-interaction

      - name: Ruff lint
        run: poetry run ruff check .

      - name: Ruff format check
        run: poetry run ruff format --check .

      - name: Mypy type check
        run: poetry run mypy app --ignore-missing-imports

      - name: Pytest
        env:
          DATABASE_URL: postgresql+asyncpg://test_user:test_pass@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0
          JWT_SECRET_KEY: test-secret-key-ci
          APP_ENV: testing
        run: poetry run pytest --cov=app --cov-report=xml -v

      - name: Coverage yükle
        if: github.event_name == 'pull_request'
        uses: codecov/codecov-action@v4
        with:
          files: backend/coverage.xml
          flags: backend

  # ── Frontend Tests ──
  frontend-test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend

    steps:
      - uses: actions/checkout@v4

      - name: pnpm kurulumu
        uses: pnpm/action-setup@v4
        with:
          version: ${{ env.PNPM_VERSION }}

      - name: Node.js kurulumu
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: pnpm
          cache-dependency-path: frontend/pnpm-lock.yaml

      - name: Bağımlılıkları kur
        run: pnpm install --frozen-lockfile

      - name: TypeScript check
        run: pnpm tsc --noEmit

      - name: ESLint
        run: pnpm lint

      - name: Vitest
        run: pnpm test -- --coverage

      - name: Build
        run: pnpm build

  # ── Docker Build ──
  docker-build:
    runs-on: ubuntu-latest
    needs: [backend-test, frontend-test]
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - name: Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Backend image build
        uses: docker/build-push-action@v6
        with:
          context: ./backend
          push: false
          tags: bist-robogo-backend:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Frontend image build
        uses: docker/build-push-action@v6
        with:
          context: ./frontend
          push: false
          tags: bist-robogo-frontend:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

---

## 5. Geliştirme Sırası — Faz Bazlı Detaylı Adımlar

### Faz 0: Altyapı Kurulumu (Hafta 1-2)

Her adımda ne yapılacak, hangi dosya oluşturulacak ve nasıl doğrulanacak belirtilmiştir.

---

#### Adım 0.1 — Proje Kök Yapısı

**Oluşturulacak dosyalar:**

```
bist-robogo/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── Makefile
├── README.md
└── scripts/
    └── init-db.sql
```

**Komutlar:**

```bash
cd c:\Projects\bist-robogo
mkdir scripts
# docker-compose.yml, .env.example, Makefile → Doküman 10 Bölüm 1'den kopyala
# .gitignore → Mevcut
# scripts/init-db.sql → Doküman 10 Bölüm 1.2'den kopyala
```

**Doğrulama:**

```bash
docker compose up -d postgres redis
docker compose ps  # postgres ve redis "healthy" olmalı
docker compose exec postgres psql -U bist_user -d bist_robogo -c "SELECT 1;"
docker compose exec redis redis-cli -a bist_redis_pass_2026 ping
```

---

#### Adım 0.2 — Backend Projesi Oluşturma

**Komutlar:**

```bash
mkdir backend
cd backend
pip install poetry
poetry init --name bist-robogo-backend --python "^3.12" --no-interaction
```

**pyproject.toml** — Doküman 07 Bölüm 23'ten kopyala.

**Bağımlılıkları kur:**

```bash
poetry install
```

**Oluşturulacak dosyalar (sırasıyla):**

```
backend/
├── pyproject.toml          # Doc 07 §23
├── poetry.lock             # poetry install ile otomatik
├── Dockerfile              # Doc 10 §2.1
├── alembic.ini             # Doc 07 §22
├── app/
│   ├── __init__.py         # boş
│   ├── config.py           # Doc 07 §2
│   ├── database.py         # Doc 07 §3
│   ├── main.py             # Doc 07 §7
│   ├── exceptions.py       # Doc 07 §9
│   ├── middleware.py        # Doc 07 §8
│   ├── dependencies.py     # Doc 07 §11
│   ├── logging_config.py   # Doc 07 §21
│   ├── models/
│   │   ├── __init__.py     # Doc 07 §6
│   │   ├── base.py         # Doc 07 §4
│   │   └── user.py         # Doc 07 §5
│   ├── schemas/
│   │   ├── __init__.py     # boş
│   │   ├── common.py       # Doc 07 §15
│   │   └── auth.py         # Doc 07 §16
│   ├── core/
│   │   ├── __init__.py     # boş
│   │   ├── security.py     # Doc 07 §10
│   │   ├── redis_client.py # Doc 07 §17
│   │   ├── rate_limiter.py # Doc 07 §18
│   │   └── websocket_manager.py # Doc 07 §19
│   ├── api/
│   │   ├── __init__.py     # boş
│   │   ├── router.py       # Doc 07 §12
│   │   ├── health.py       # Doc 07 §13
│   │   └── v1/
│   │       ├── __init__.py # boş
│   │       └── auth.py     # Doc 07 §14
│   ├── services/
│   │   └── __init__.py     # boş (§Doc 07 servis pattern'ı)
│   ├── repositories/
│   │   └── __init__.py     # boş (Doc 07 repository pattern'ı)
│   ├── brokers/
│   │   ├── __init__.py     # boş
│   │   ├── base.py         # Doc 07 §23.1
│   │   ├── paper_broker.py # Doc 07 §23.2
│   │   └── factory.py      # Doc 07 §23.3
│   ├── indicators/
│   │   ├── __init__.py     # boş
│   │   └── momentum.py     # Doc 07 §24
│   ├── tasks/
│   │   ├── __init__.py     # boş
│   │   ├── celery_app.py   # Doc 07 §20.1
│   │   └── market_tasks.py # Doc 07 §20.2
│   ├── websocket/
│   │   ├── __init__.py     # boş
│   │   └── market_stream.py # Doc 07 §19.2
│   └── utils/
│       ├── __init__.py     # boş
│       ├── constants.py    # Doc 07 §25.1
│       └── formatters.py   # Doc 07 §25.2
├── alembic/
│   ├── env.py              # Doc 07 §22
│   └── versions/           # boş klasör
├── scripts/
│   └── seed_symbols.py     # Doc 07 §24 (seed)
└── tests/
    ├── __init__.py          # boş
    └── conftest.py          # Doc 07 §25 (test fixtures)
```

**Doğrulama:**

```bash
cd backend
poetry run python -c "from app.config import settings; print(settings.APP_NAME)"
# Çıktı: bist-robogo
```

---

#### Adım 0.3 — Alembic Migrasyon

```bash
cd backend
poetry run alembic revision --autogenerate -m "initial_tables"
poetry run alembic upgrade head
```

**Doğrulama:**

```bash
docker compose exec postgres psql -U bist_user -d bist_robogo -c "\dt"
# users, api_keys tablolarını görmeli
```

---

#### Adım 0.4 — Backend Çalıştırma

```bash
cd backend
poetry run uvicorn app.main:app --reload --port 8000
```

**Doğrulama:**

```bash
curl http://localhost:8000/api/health
# {"status":"healthy","timestamp":"...","version":"1.0.0","services":{"database":"ok","redis":"ok"}}

curl http://localhost:8000/docs
# Swagger UI açılmalı
```

---

#### Adım 0.5 — Frontend Projesi Oluşturma

```bash
cd c:\Projects\bist-robogo
pnpm create next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
cd frontend
pnpm dlx shadcn@latest init
```

shadcn init soruları:

- Style: Default
- Base color: Slate
- CSS variables: Yes

**shadcn bileşenlerini kur:**

```bash
pnpm dlx shadcn@latest add button card input label select textarea dialog sheet dropdown-menu popover tooltip table tabs badge separator progress slider switch checkbox alert toast sonner avatar skeleton scroll-area command form navigation-menu collapsible accordion
```

**Ek bağımlılıklar:**

```bash
pnpm add @tanstack/react-query@^5.62 zustand@^5.0 socket.io-client@^4.8
pnpm add lightweight-charts@^4.2 recharts@^2.15 @tremor/react@^3.18
pnpm add axios@^1.7 zod@^3.24 react-hook-form@^7.54 @hookform/resolvers@^3.9
pnpm add date-fns@^4.1 clsx@^2.1 tailwind-merge@^2.6 class-variance-authority@^0.7
pnpm add lucide-react@^0.468 next-themes@^0.4 nuqs@^2.0
pnpm add -D vitest@^2.1 @testing-library/react@^16.1 @testing-library/jest-dom@^6.6
pnpm add -D playwright@^1.49 prettier@^3.4 prettier-plugin-tailwindcss@^0.6
```

---

#### Adım 0.6 — Frontend Yapılandırma

**Oluşturulacak/güncellenecek dosyalar (sırasıyla):**

```
frontend/
├── next.config.ts              # Doc 08 §2.1
├── tailwind.config.ts          # Doc 08 §2.2
├── src/
│   ├── app/
│   │   ├── globals.css         # Doc 08 §2.3
│   │   └── layout.tsx          # Doc 08 §7.1
│   ├── lib/
│   │   ├── utils.ts            # Doc 08 §10.1
│   │   ├── utils/
│   │   │   └── formatters.ts   # Doc 08 §10.2
│   │   └── api/
│   │       ├── client.ts       # Doc 08 §3.1
│   │       ├── market.ts       # Doc 08 §3.2
│   │       └── orders.ts       # Doc 08 §3.3
│   ├── types/
│   │   ├── market.ts           # Doc 08 §4.1
│   │   ├── order.ts            # Doc 08 §4.2
│   │   ├── portfolio.ts        # Doc 08 §4.3
│   │   └── strategy.ts         # Doc 08 §4.4
│   ├── stores/
│   │   ├── auth-store.ts       # Doc 08 §5.1
│   │   ├── market-store.ts     # Doc 08 §5.2
│   │   └── ui-store.ts         # Doc 08 §5.3
│   ├── hooks/
│   │   ├── use-websocket.ts    # Doc 08 §6.1
│   │   ├── use-market-data.ts  # Doc 08 §6.2
│   │   └── use-portfolio.ts    # Doc 08 §6.3
│   └── components/
│       ├── providers/
│       │   ├── theme-provider.tsx  # Doc 08 §7.2
│       │   └── query-provider.tsx  # Doc 08 §7.3
│       ├── auth/
│       │   └── auth-guard.tsx      # Doc 08 §11.1
│       └── layout/
│           ├── sidebar.tsx         # Doc 08 §7.5
│           └── header.tsx          # Doc 08 §7.6
```

**Doğrulama:**

```bash
cd frontend
pnpm build  # Hatasız bitmelidir
pnpm dev    # http://localhost:3000 açılmalı
```

---

### Faz 1: MVP — Temel Özellikler (Hafta 3-8)

#### Sprint 1.1 (Hafta 3-4): Auth + Dashboard

| #   | Görev                                                    | Dosya                                                                     | Referans       |
| --- | -------------------------------------------------------- | ------------------------------------------------------------------------- | -------------- |
| 1   | Auth API endpoint (register, login, refresh, logout, me) | `backend/app/api/v1/auth.py`                                              | Doc 07 §14     |
| 2   | Auth servis                                              | `backend/app/services/auth_service.py`                                    | Doc 07 pattern |
| 3   | User repository                                          | `backend/app/repositories/user_repository.py`                             | Doc 07 pattern |
| 4   | Login sayfası                                            | `frontend/src/app/(auth)/login/page.tsx`                                  | Doc 09 §14.1   |
| 5   | Register sayfası                                         | `frontend/src/app/(auth)/register/page.tsx`                               | —              |
| 6   | Auth layout                                              | `frontend/src/app/(auth)/layout.tsx`                                      | —              |
| 7   | Dashboard layout                                         | `frontend/src/app/(dashboard)/layout.tsx`                                 | Doc 08 §7.4    |
| 8   | Dashboard sayfa                                          | `frontend/src/app/(dashboard)/dashboard/page.tsx`                         | Doc 08 §8.2    |
| 9   | StatCard bileşeni                                        | `frontend/src/components/dashboard/stat-card.tsx`                         | Doc 08 §8.1    |
| 10  | DashboardStats                                           | `frontend/src/app/(dashboard)/dashboard/_components/dashboard-stats.tsx`  | —              |
| 11  | EquityCurve                                              | `frontend/src/app/(dashboard)/dashboard/_components/equity-curve.tsx`     | —              |
| 12  | AllocationChart                                          | `frontend/src/app/(dashboard)/dashboard/_components/allocation-chart.tsx` | —              |

**Doğrulama:**

```bash
# Backend auth test
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test123456!","full_name":"Test User"}'
# 201

curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test123456!"}'
# 200 + access_token

# Frontend kontrol
# http://localhost:3000/login → Login formu görünmeli
# Giriş sonrası → /dashboard'a yönlenmeli
```

---

#### Sprint 1.2 (Hafta 5-6): Piyasa Verisi + Grafik

| #   | Görev                            | Dosya                                                   | Referans     |
| --- | -------------------------------- | ------------------------------------------------------- | ------------ |
| 1   | Symbol modeli                    | `backend/app/models/symbol.py`                          | Doc 03 SQL   |
| 2   | OHLCV modeli                     | `backend/app/models/ohlcv.py`                           | Doc 03 SQL   |
| 3   | TimescaleDB hypertable migration | `alembic/versions/002_market_data.py`                   | Doc 03       |
| 4   | Market API endpoints             | `backend/app/api/v1/market.py`                          | Doc 03 API   |
| 5   | Market servis                    | `backend/app/services/market_service.py`                | —            |
| 6   | Veri çekme task'ı                | `backend/app/tasks/market_tasks.py`                     | Doc 07 §20.2 |
| 7   | Seed data script çalıştır        | `scripts/seed_symbols.py`                               | Doc 07 §24   |
| 8   | Sembol listesi sayfası           | `frontend/src/app/(dashboard)/market/page.tsx`          | Doc 09 §14.3 |
| 9   | SymbolTable bileşeni             | `frontend/src/components/market/symbol-table.tsx`       | —            |
| 10  | Sembol detay sayfası             | `frontend/src/app/(dashboard)/market/[symbol]/page.tsx` | —            |
| 11  | CandlestickChart                 | `frontend/src/components/charts/candlestick-chart.tsx`  | Doc 08 §9.1  |
| 12  | WebSocket bağlantısı             | `frontend/src/hooks/use-websocket.ts`                   | Doc 08 §6.1  |
| 13  | WebSocket endpoint               | `backend/app/websocket/market_stream.py`                | Doc 07 §19.2 |

**Doğrulama:**

```bash
# Seed data
cd backend && poetry run python scripts/seed_symbols.py

# API kontrol
curl http://localhost:8000/api/v1/market/symbols
# 30 sembol dönmeli

curl http://localhost:8000/api/v1/market/symbols/THYAO/history?interval=1d&limit=30
# OHLCV verisi dönmeli

# Frontend: /market sayfası yüklenmeli, tablo görünmeli
# /market/THYAO → Candlestick grafik görünmeli
```

---

#### Sprint 1.3 (Hafta 7-8): Paper Trading + Portföy

| #   | Görev                                           | Dosya                                                 | Referans     |
| --- | ----------------------------------------------- | ----------------------------------------------------- | ------------ |
| 1   | Order modeli                                    | `backend/app/models/order.py`                         | Doc 03 SQL   |
| 2   | Position modeli                                 | `backend/app/models/position.py`                      | Doc 03 SQL   |
| 3   | Portfolio modeli                                | `backend/app/models/portfolio.py`                     | Doc 03 SQL   |
| 4   | Trade modeli                                    | `backend/app/models/trade.py`                         | Doc 03 SQL   |
| 5   | Migration: order + position + portfolio + trade | `alembic/versions/003_trading.py`                     | —            |
| 6   | Order API endpoints                             | `backend/app/api/v1/orders.py`                        | Doc 03 API   |
| 7   | Portfolio API endpoints                         | `backend/app/api/v1/portfolio.py`                     | Doc 03 API   |
| 8   | Trading servis                                  | `backend/app/services/trading_service.py`             | —            |
| 9   | Risk manager servis                             | `backend/app/services/risk_service.py`                | —            |
| 10  | Paper broker kullan                             | `backend/app/brokers/paper_broker.py`                 | Doc 07 §23.2 |
| 11  | Order form bileşeni                             | `frontend/src/components/market/order-form.tsx`       | Doc 09 §14.3 |
| 12  | Emirler sayfası                                 | `frontend/src/app/(dashboard)/orders/page.tsx`        | —            |
| 13  | Portföy sayfası                                 | `frontend/src/app/(dashboard)/portfolio/page.tsx`     | —            |
| 14  | Pozisyon bileşeni                               | `frontend/src/components/portfolio/position-card.tsx` | —            |

**Doğrulama:**

```bash
# Emir ver (Paper)
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"THYAO","side":"buy","order_type":"market","quantity":100}'
# 201 + order detayı

# Portföy kontrol
curl http://localhost:8000/api/v1/portfolio/summary \
  -H "Authorization: Bearer <token>"
# Portföy özeti dönmeli
```

---

### Faz 2: Genişleme (Hafta 9-14)

#### Sprint 2.1 (Hafta 9-10): Trend Analiz

| #   | Görev                                                                                 |
| --- | ------------------------------------------------------------------------------------- |
| 1   | Teknik indikatör hesaplama servisi (RSI, MACD, Bollinger, EMA)                        |
| 2   | Trend tespit servisi (destek/direnç, breakout, hacim analizi)                         |
| 3   | Trend API endpoints (`/api/v1/trends/candidates`, `/api/v1/trends/analysis/{symbol}`) |
| 4   | Trend sayfası — adaylar tablosu, filtreleme                                           |
| 5   | Trend detay sayfası — sembol bazlı tam analiz                                         |
| 6   | Celery task: günlük trend taraması                                                    |

#### Sprint 2.2 (Hafta 11-12): Strateji Motoru

| #   | Görev                                                       |
| --- | ----------------------------------------------------------- |
| 1   | Strategy modeli + migration                                 |
| 2   | Signal modeli + migration                                   |
| 3   | BaseStrategy abstract sınıfı                                |
| 4   | MovingAverageCross stratejisi implementasyonu               |
| 5   | RSI Over-Sold/Bought stratejisi implementasyonu             |
| 6   | Strategy API endpoints (CRUD + activate/deactivate)         |
| 7   | Signal API endpoints (list + latest)                        |
| 8   | Celery task: strateji değerlendirme (her 5 dk)              |
| 9   | Stratejiler sayfası — liste, oluşturma, parametre düzenleme |
| 10  | Strateji detay — sinyal geçmişi, performans metrikleri      |

#### Sprint 2.3 (Hafta 13-14): Backtest

| #   | Görev                                                                       |
| --- | --------------------------------------------------------------------------- |
| 1   | Backtest modeli + migration                                                 |
| 2   | Backtest engine (vektörel hesaplama, komisyon simülasyonu)                  |
| 3   | Backtest API endpoints (create, get, list, compare)                         |
| 4   | Backtest parametreleri: başlangıç sermaye, komisyon oranı, slippage         |
| 5   | Backtest metrikleri: Sharpe, Sortino, max drawdown, win rate, profit factor |
| 6   | Celery task: async backtest çalıştırma                                      |
| 7   | Backtest sayfası — parametre formu, sonuçlar                                |
| 8   | Backtest sonuç grafiği — equity curve overlay                               |

---

### Faz 3: AI/ML Entegrasyonu (Hafta 15-22)

| Sprint | Görev                                                                   |
| ------ | ----------------------------------------------------------------------- |
| 3.1    | Feature engineering pipeline (TA-Lib, pandas-ta ile 50+ teknik özellik) |
| 3.2    | XGBoost / LightGBM model eğitimi (yön tahmini)                          |
| 3.3    | Optuna ile hiperparametre optimizasyonu                                 |
| 3.4    | MLflow model versiyonlama                                               |
| 3.5    | ONNX Runtime ile model serving                                          |
| 3.6    | AI strateji: ML tabanlı sinyal üretimi                                  |
| 3.7    | Model performans dashboard'u                                            |
| 3.8    | A/B test altyapısı (eski strateji vs. ML strateji)                      |

---

### Faz 4: Ölçekleme ve Prodüksiyon (Hafta 23+)

| Sprint | Görev                                               |
| ------ | --------------------------------------------------- |
| 4.1    | Gerçek broker entegrasyonu (Matriks/İş Yatırım API) |
| 4.2    | Kafka event streaming                               |
| 4.3    | Prometheus + Grafana monitoring                     |
| 4.4    | Kubernetes deployment (Helm charts)                 |
| 4.5    | Performans optimizasyonu + yük testi                |
| 4.6    | SPK/KVKK uyumluluk kontrolleri                      |

---

## 6. Doğrulama Kontrol Listesi

Her sprint sonunda aşağıdaki kontroller yapılmalıdır:

### 6.1 Backend Kontrolleri

```bash
# Lint
cd backend && poetry run ruff check .
# 0 hata olmalı

# Format
poetry run ruff format --check .
# Tüm dosyalar formatlanmış olmalı

# Type check
poetry run mypy app --ignore-missing-imports
# 0 hata olmalı

# Test
poetry run pytest --cov=app -v
# Tüm testler geçmeli, coverage > %70

# Migration
poetry run alembic upgrade head
# Hatasız tamamlanmalı

# Health check
curl http://localhost:8000/api/health
# {"status":"healthy",...}
```

### 6.2 Frontend Kontrolleri

```bash
# TypeScript
cd frontend && pnpm tsc --noEmit
# 0 hata olmalı

# ESLint
pnpm lint
# 0 uyarı / 0 hata olmalı

# Build
pnpm build
# Hatasız tamamlanmalı

# Test
pnpm test
# Tüm testler geçmeli
```

### 6.3 Docker Kontrolleri

```bash
# Tüm servisler çalışıyor mu
docker compose ps
# postgres, redis, backend, frontend → "Up" ve "healthy"

# Backend log kontrol
docker compose logs backend --tail 20
# Hata satırı olmamalı

# Frontend erişim
curl http://localhost:3000
# HTML dönmeli
```

---

## 7. Dosya İçerik Referans Haritası

Aşağıdaki tablo, her dosyanın içeriğinin hangi dokümanda ve hangi bölümde tanımlandığını gösterir. AI Agent bu tabloyu kullanarak doğru içeriği bulabilir.

| Dosya Yolu                                             | Doküman | Bölüm      |
| ------------------------------------------------------ | ------- | ---------- |
| `docker-compose.yml`                                   | Doc 10  | §1.1       |
| `scripts/init-db.sql`                                  | Doc 10  | §1.2       |
| `backend/Dockerfile`                                   | Doc 10  | §2.1       |
| `frontend/Dockerfile`                                  | Doc 10  | §3.1       |
| `.github/workflows/ci.yml`                             | Doc 10  | §4.1       |
| `backend/pyproject.toml`                               | Doc 07  | §23        |
| `backend/alembic.ini`                                  | Doc 07  | §22        |
| `backend/alembic/env.py`                               | Doc 07  | §22        |
| `backend/app/config.py`                                | Doc 07  | §2         |
| `backend/app/database.py`                              | Doc 07  | §3         |
| `backend/app/main.py`                                  | Doc 07  | §7         |
| `backend/app/middleware.py`                            | Doc 07  | §8         |
| `backend/app/exceptions.py`                            | Doc 07  | §9         |
| `backend/app/dependencies.py`                          | Doc 07  | §11        |
| `backend/app/logging_config.py`                        | Doc 07  | §21        |
| `backend/app/models/base.py`                           | Doc 07  | §4         |
| `backend/app/models/user.py`                           | Doc 07  | §5         |
| `backend/app/models/__init__.py`                       | Doc 07  | §6         |
| `backend/app/schemas/common.py`                        | Doc 07  | §15        |
| `backend/app/schemas/auth.py`                          | Doc 07  | §16        |
| `backend/app/core/security.py`                         | Doc 07  | §10        |
| `backend/app/core/redis_client.py`                     | Doc 07  | §17        |
| `backend/app/core/rate_limiter.py`                     | Doc 07  | §18        |
| `backend/app/core/websocket_manager.py`                | Doc 07  | §19        |
| `backend/app/api/router.py`                            | Doc 07  | §12        |
| `backend/app/api/health.py`                            | Doc 07  | §13        |
| `backend/app/api/v1/auth.py`                           | Doc 07  | §14        |
| `backend/app/websocket/market_stream.py`               | Doc 07  | §19.2      |
| `backend/app/tasks/celery_app.py`                      | Doc 07  | §20.1      |
| `backend/app/tasks/market_tasks.py`                    | Doc 07  | §20.2      |
| `backend/app/brokers/base.py`                          | Doc 07  | §23.1      |
| `backend/app/brokers/paper_broker.py`                  | Doc 07  | §23.2      |
| `backend/app/brokers/factory.py`                       | Doc 07  | §23.3      |
| `backend/app/indicators/momentum.py`                   | Doc 07  | §24        |
| `backend/app/utils/constants.py`                       | Doc 07  | §25.1      |
| `backend/app/utils/formatters.py`                      | Doc 07  | §25.2      |
| `backend/scripts/seed_symbols.py`                      | Doc 07  | §24 (seed) |
| `backend/tests/conftest.py`                            | Doc 07  | §25 (test) |
| `frontend/next.config.ts`                              | Doc 08  | §2.1       |
| `frontend/tailwind.config.ts`                          | Doc 08  | §2.2       |
| `frontend/src/app/globals.css`                         | Doc 08  | §2.3       |
| `frontend/src/app/layout.tsx`                          | Doc 08  | §7.1       |
| `frontend/src/app/(dashboard)/layout.tsx`              | Doc 08  | §7.4       |
| `frontend/src/lib/utils.ts`                            | Doc 08  | §10.1      |
| `frontend/src/lib/utils/formatters.ts`                 | Doc 08  | §10.2      |
| `frontend/src/lib/api/client.ts`                       | Doc 08  | §3.1       |
| `frontend/src/lib/api/market.ts`                       | Doc 08  | §3.2       |
| `frontend/src/lib/api/orders.ts`                       | Doc 08  | §3.3       |
| `frontend/src/types/market.ts`                         | Doc 08  | §4.1       |
| `frontend/src/types/order.ts`                          | Doc 08  | §4.2       |
| `frontend/src/types/portfolio.ts`                      | Doc 08  | §4.3       |
| `frontend/src/types/strategy.ts`                       | Doc 08  | §4.4       |
| `frontend/src/stores/auth-store.ts`                    | Doc 08  | §5.1       |
| `frontend/src/stores/market-store.ts`                  | Doc 08  | §5.2       |
| `frontend/src/stores/ui-store.ts`                      | Doc 08  | §5.3       |
| `frontend/src/hooks/use-websocket.ts`                  | Doc 08  | §6.1       |
| `frontend/src/hooks/use-market-data.ts`                | Doc 08  | §6.2       |
| `frontend/src/hooks/use-portfolio.ts`                  | Doc 08  | §6.3       |
| `frontend/src/components/providers/theme-provider.tsx` | Doc 08  | §7.2       |
| `frontend/src/components/providers/query-provider.tsx` | Doc 08  | §7.3       |
| `frontend/src/components/auth/auth-guard.tsx`          | Doc 08  | §11.1      |
| `frontend/src/components/layout/sidebar.tsx`           | Doc 08  | §7.5       |
| `frontend/src/components/layout/header.tsx`            | Doc 08  | §7.6       |
| `frontend/src/components/dashboard/stat-card.tsx`      | Doc 08  | §8.1       |
| `frontend/src/app/(dashboard)/dashboard/page.tsx`      | Doc 08  | §8.2       |
| `frontend/src/components/charts/candlestick-chart.tsx` | Doc 08  | §9.1       |

---

_Bu doküman, bist-robogo projesinin sıfırdan prodüksiyona kadar tüm geliştirme adımlarını tanımlar. AI Agent bu rehberi takip ederek projeyi hatasız geliştirebilir._
