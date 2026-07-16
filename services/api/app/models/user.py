"""
SQLAlchemy ORM — Users table.
"""
import uuid
from sqlalchemy import Column, String, JSON, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)

    # Voice personalisation
    voice_id = Column(String, default="21m00Tcm4TlvDq8ikWAM")   # ElevenLabs Rachel
    preferences = Column(JSON, default=dict)                     # {"tone": "casual"}

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
