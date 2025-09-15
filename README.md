# SoulSeer Monorepo

[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy?type=git&repository=github.com/EmilynnJ/WARPSEER&branch=main&ports=8080;http;/&env[DATABASE_URL]=CHANGE_ME&env[CLERK_SECRET_KEY]=CHANGE_ME&env[STRIPE_SECRET_KEY]=CHANGE_ME&env[PUBLIC_CLERK_PUBLISHABLE_KEY]=CHANGE_ME&env[PUBLIC_STRIPE_PUBLIC_KEY]=CHANGE_ME)

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

## 🚀 Deploy to Production

### One-Click Deploy to Koyeb (FREE)

1. Click the "Deploy to Koyeb" button above
2. Sign in with GitHub (no credit card required)
3. Fill in your environment variables:
   - `DATABASE_URL`: Your Neon PostgreSQL connection string
   - `CLERK_SECRET_KEY`: From Clerk Dashboard → API Keys
   - `STRIPE_SECRET_KEY`: From Stripe Dashboard → Developers → API Keys
   - `PUBLIC_CLERK_PUBLISHABLE_KEY`: From Clerk Dashboard → API Keys
   - `PUBLIC_STRIPE_PUBLIC_KEY`: From Stripe Dashboard → Developers → API Keys
   - `STRIPE_WEBHOOK_SECRET`: From Stripe Dashboard → Webhooks (optional)
4. Click "Deploy"!

Your app will be live at `https://[your-app-name].koyeb.app` in ~3 minutes.

### Manual Deployment

#### Prerequisites
- GitHub account connected to Koyeb
- Environment variables ready

#### Steps
1. Fork or push this repo to your GitHub
2. Go to [app.koyeb.com](https://app.koyeb.com)
3. Click "Create App" → "GitHub"
4. Select your repository
5. Koyeb auto-detects the Dockerfile
6. Set port to `8080`
7. Add environment variables
8. Select "nano" instance (free tier)
9. Deploy!

### Features on Koyeb
- ✅ Auto-deploy on Git push
- ✅ WebSocket support for real-time features
- ✅ Custom domains with SSL
- ✅ Zero-downtime deployments
- ✅ Built-in health checks
- ✅ 512MB RAM free tier

### Architecture
```
Nginx (port 8080)
├── /api/* → FastAPI Backend (port 8000)
└── /* → SvelteKit Frontend (port 3000)
```

All services run in a single container managed by supervisord.
