# SoulSeer Monorepo

This repo contains:
- apps/frontend: SvelteKit + Tailwind + TypeScript + Clerk + PWA
- apps/backend: FastAPI + SQLAlchemy + Alembic + Redis + Stripe + WebSockets
- apps/worker: Celery worker for billing ticks and daily payouts
- packages/shared: Shared schemas and types
- infra: Docker and deployment configs

Quick start (Windows PowerShell)
1) Prerequisites
- Node.js LTS and pnpm
- Python 3.11+
- Docker Desktop (recommended for Redis)

2) Install frontend deps
- pnpm -w install

3) Backend Python venv
- python -m venv .venv
- .venv/Scripts/Activate.ps1
- pip install -r apps/backend/requirements.txt

4) Environment
- Copy .env.example to .env at repo root and fill values (use test keys in dev).

5) Run services
- Redis: docker run -p 6379:6379 redis:7-alpine
- Backend API: uvicorn apps.backend.src.soulseer.main:app --host 0.0.0.0 --port 8000 --reload
- Celery worker: celery -A apps.backend.src.soulseer.celery_app.celery worker -B -l info
- Frontend: pnpm --filter @soulseer/frontend dev

6) Open
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/docs

Notes
- Do not commit real secrets. Use .env and platform secret managers.
- Frontend will call backend at BACKEND_API_BASE (set in .env).
- Clerk JWTs are verified in backend via JWKS.
- Neon Postgres is the source of truth; Redis for presence/rate limiting.
