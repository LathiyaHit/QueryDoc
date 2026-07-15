"""
Centralised settings using Pydantic-settings.
All values are read from environment variables / .env file.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
env_file_paths = [
    Path.cwd() / ".env",  # current directory
    Path.cwd().parent / ".env",  # parent directory
    Path.cwd().parent.parent / ".env",  # grandparent directory
]

for env_file_path in env_file_paths:
    if env_file_path.exists():
        load_dotenv(env_file_path, override=True)
        break


class Settings(BaseSettings):
    # ── App ────────────────────────────────────────────────────
    APP_ENV: str = "development"
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # ── Database ───────────────────────────────────────────────
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

    # ── AI Services ────────────────────────────────────────────
    GROQ_API_KEY: str = Field(..., env="GROQ_API_KEY")
    DEEPGRAM_API_KEY: str  = Field(..., env="DEEPGRAM_API_KEY")
    ELEVENLABS_API_KEY: str = Field(..., env="ELEVENLABS_API_KEY")

   # ── Vector DB ──────────────────────────────────────────────
    QDRANT_URL: str = Field(default="http://localhost:6333", env="QDRANT_URL")
    QDRANT_COLLECTION: str = Field(default="user_memories", env="QDRANT_COLLECTION")

    # ── RAG (document knowledge base) ───────────────────────────
    RAG_QDRANT_COLLECTION: str = Field(default="rag_documents", env="RAG_QDRANT_COLLECTION")
    RAG_DOCS_DIR: str = Field(default="data/rag_docs", env="RAG_DOCS_DIR")
    RAG_CHUNK_SIZE: int = Field(default=1000, env="RAG_CHUNK_SIZE")
    RAG_CHUNK_OVERLAP: int = Field(default=200, env="RAG_CHUNK_OVERLAP")
    RAG_TOP_K: int = Field(default=5, env="RAG_TOP_K")
    RAG_MIN_SCORE: float = Field(default=0.2, env="RAG_MIN_SCORE")

    # ── Observability ──────────────────────────────────────────
    LANGFUSE_PUBLIC_KEY: str = Field(default="", env="LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SECRET_KEY: str = Field(default="", env="LANGFUSE_SECRET_KEY")
    LANGFUSE_HOST: str = Field(default="http://localhost:3000", env="LANGFUSE_HOST")
    SENTRY_DSN: str = Field(default="", env="SENTRY_DSN")
    OTEL_ENDPOINT: str = Field(
        default="http://localhost:4317", env="OTEL_EXPORTER_OTLP_ENDPOINT"
    )

    class Config:
        env_file_encoding = "utf-8"


settings = Settings()
