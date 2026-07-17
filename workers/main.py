"""Celery application — background task worker."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../services/api"))

from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "voice_workers",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["tasks.memory_extraction", "tasks.analytics", "tasks.cleanup"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "tasks.memory_extraction.*": {"queue": "memory"},
        "tasks.analytics.*": {"queue": "analytics"},
    },
)
