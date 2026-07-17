"""Aggregate daily session analytics."""
from workers.main import celery_app


@celery_app.task(name="tasks.analytics.aggregate_daily")
def aggregate_daily():
    """Run nightly via Celery beat to compute daily latency averages."""
    pass  # implement: query voice_sessions, write to analytics table
