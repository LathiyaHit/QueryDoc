"""
FastAPI application entrypoint.
Registers all routers, middleware, and lifespan events.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
# from app.core.telemetry import setup_telemetry  # TODO: Fix pkg_resources dependency
from app.api.routes import health, users, voice, documents
from app.services.rag.rag_vector_store import RagVectorStore

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    await init_db()
    await RagVectorStore().ensure_collection()
    yield

app = FastAPI(
    title="Voice Assistant API",
    description="Personalised AI-powered voice assistant — ultra-low latency",
    version="1.0.0",
    lifespan=lifespan,
)

# ── Telemetry (must be before routes) ──────────────────────────
# setup_telemetry(app)  # TODO: Fix pkg_resources dependency

# ── CORS ───────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────
app.include_router(health.router,     prefix="/health", tags=["health"])
app.include_router(voice.router,      prefix="/api/v1/voice", tags=["voice"])
app.include_router(users.router,      prefix="/api/v1/users", tags=["users"])
app.include_router(documents.router,  prefix="/api/v1/documents", tags=["documents"])
