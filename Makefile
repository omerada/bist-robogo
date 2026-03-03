.PHONY: help dev up down logs test lint migrate seed

# ─── Yardım ───
help: ## Bu yardım mesajını gösterir
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ─── Geliştirme ───
dev: ## Tüm servisleri geliştirme modunda başlat
	docker-compose -f infra/docker/docker-compose.dev.yml up -d

up: ## Tüm servisleri başlat
	docker-compose -f infra/docker/docker-compose.yml up -d

down: ## Tüm servisleri durdur
	docker-compose -f infra/docker/docker-compose.yml down

logs: ## Docker loglarını göster
	docker-compose -f infra/docker/docker-compose.yml logs -f

# ─── Backend ───
backend-install: ## Backend bağımlılıklarını yükle
	cd backend && poetry install

backend-dev: ## Backend'i geliştirme modunda çalıştır
	cd backend && poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

backend-test: ## Backend testlerini çalıştır
	cd backend && poetry run pytest -v --cov=app

backend-lint: ## Backend lint kontrolü
	cd backend && poetry run ruff check . && poetry run mypy .

# ─── Frontend ───
frontend-install: ## Frontend bağımlılıklarını yükle
	cd frontend && pnpm install

frontend-dev: ## Frontend'i geliştirme modunda çalıştır
	cd frontend && pnpm dev

frontend-test: ## Frontend testlerini çalıştır
	cd frontend && pnpm test

frontend-lint: ## Frontend lint kontrolü
	cd frontend && pnpm lint

frontend-build: ## Frontend'i derle
	cd frontend && pnpm build

# ─── Database ───
migrate: ## Veritabanı migrasyonlarını çalıştır
	cd backend && poetry run alembic upgrade head

migrate-create: ## Yeni migrasyon oluştur (NAME gerekli)
	cd backend && poetry run alembic revision --autogenerate -m "$(NAME)"

seed: ## Veritabanına test verisi yükle
	cd backend && poetry run python scripts/seed_data.py

# ─── Test ───
test: backend-test frontend-test ## Tüm testleri çalıştır

lint: backend-lint frontend-lint ## Tüm lint kontrollerini çalıştır

# ─── Veri ───
fetch-history: ## Geçmiş veri çek
	cd backend && poetry run python scripts/fetch_historical.py

# ─── Temizlik ───
clean: ## Geçici dosyaları temizle
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .next -exec rm -rf {} + 2>/dev/null || true
