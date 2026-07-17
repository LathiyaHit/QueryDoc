"""Prune stale sessions and old memory records."""
from workers.main import celery_app


@celery_app.task(name="tasks.cleanup.prune_old_sessions")
def prune_old_sessions(days: int = 30):
    """Delete sessions older than `days` days."""
    pass  # implement: DELETE FROM voice_sessions WHERE ended_at < now() - interval
