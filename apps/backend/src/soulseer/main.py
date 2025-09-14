from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .db import Base, engine
from .routers import health as health_router
from .routers import users as users_router
from .routers import admin as admin_router
from .routers import payments as payments_router
from .routers import sessions as sessions_router
from .routers import connect as connect_router
from .routers import readers as readers_router
from .routers import streams as streams_router
from .routers import signaling as signaling_router
import sentry_sdk

if settings.sentry_dsn_backend:
    sentry_sdk.init(dsn=settings.sentry_dsn_backend, traces_sample_rate=0.2)

# Create tables (for first run; in prod use Alembic migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(health_router.router)
app.include_router(streams_router.router)
from .routers import cms as cms_router
app.include_router(cms_router.router)
app.include_router(admin_router.router)
app.include_router(payments_router.router)
app.include_router(sessions_router.router)
app.include_router(readers_router.router)
app.include_router(streams_router.router)
app.include_router(signaling_router.router)
app.include_router(connect_router.router)

@app.get("/")
def root():
    return {"name": settings.app_name, "status": "ok"}