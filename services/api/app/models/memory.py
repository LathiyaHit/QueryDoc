"""
SQLAlchemy ORM — MemoryRecord table.
Stores raw facts extracted from conversations (mirrors Qdrant payload).
"""
import uuid
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class MemoryRecord(Base):
    __tablename__ = "memory_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    text = Column(String, nullable=False)
    category = Column(String, default="general")   # preference | habit | goal | context
    qdrant_id = Column(String, nullable=True)       # ID of corresponding Qdrant point
    created_at = Column(DateTime, server_default=func.now())
