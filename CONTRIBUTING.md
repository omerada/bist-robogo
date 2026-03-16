# Contributing to BIST RoboGo

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## 🚀 Getting Started

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create a branch** for your feature or fix

```bash
git clone https://github.com/omerada/bist-robogo.git
cd bist-robogo
git checkout -b feature/your-feature-name
```

## 🛠️ Development Setup

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ & Poetry
- Node.js 20+ & pnpm

### Quick Setup

```bash
cp .env.example .env
# Edit .env with your local settings

# Option A: Docker (recommended)
docker compose up -d --build

# Option B: Local
cd backend && poetry install
cd frontend && pnpm install
```

## 📝 Code Guidelines

### Backend (Python)

- Follow [PEP 8](https://peps.python.org/pep-0008/) style
- Use type hints everywhere
- Run linter before committing:
  ```bash
  cd backend
  poetry run ruff check app/ tests/
  poetry run ruff format app/ tests/
  ```

### Frontend (TypeScript)

- Use TypeScript strictly (no `any`)
- Follow the existing component patterns
- Run lint before committing:
  ```bash
  cd frontend
  pnpm lint
  pnpm exec tsc --noEmit
  ```

## 🧪 Testing

All changes must include tests. The CI pipeline must pass before merging.

```bash
# Backend tests
cd backend && poetry run pytest -v --cov=app

# Frontend tests
cd frontend && pnpm test

# E2E tests
cd frontend && pnpm test:e2e
```

## 📦 Pull Request Process

1. Ensure your code passes all tests and linting
2. Update documentation if needed
3. Write a clear PR description explaining **what** and **why**
4. Reference any related issues (e.g., `Closes #123`)
5. Request review from maintainers

### PR Title Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat: add RSI strategy backtesting`
- `fix: correct daily P&L calculation`
- `docs: update API documentation`
- `test: add risk service unit tests`
- `refactor: simplify order execution flow`

## 🐛 Bug Reports

When reporting bugs, please include:

- Steps to reproduce
- Expected vs actual behavior
- Environment (OS, Python/Node version, Docker version)
- Relevant logs or screenshots

## 💡 Feature Requests

Feature requests are welcome! Please open an issue with:

- Clear description of the feature
- Use case / motivation
- Proposed implementation approach (optional)

## 🔒 Security

If you discover a security vulnerability, please **do not** open a public issue. See [SECURITY.md](SECURITY.md) for responsible disclosure instructions.

## 📄 License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
