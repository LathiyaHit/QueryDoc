"""
SQLAlchemy ORM — VoiceSession table.
Each WebSocket connection = one session row.
"""
import uuid
from sqlalchemy import Column, String, Float, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class VoiceSession(Base):
    __tablename__ = "voice_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    started_at = Column(DateTime, server_default=func.now())
    ended_at = Column(DateTime, nullable=True)

    # Latency metrics (milliseconds)
    avg_latency_ms = Column(Float, nullable=True)
    turn_count = Column(Float, default=0)
