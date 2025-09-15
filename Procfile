web: cd apps/backend && uvicorn src.soulseer.main:app --host 0.0.0.0 --port $PORT
worker: cd apps/backend && celery -A src.soulseer.celery_app worker --loglevel=info
frontend: cd apps/frontend && npm run preview -- --port ${FRONTEND_PORT:-3000}