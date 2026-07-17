"""Pydantic request / response schemas for User endpoints."""
from pydantic import BaseModel, EmailStr
from uuid import UUID


class UserCreate(BaseModel):
    email: EmailStr
    name: str | None = None
    password: str


class UserRead(BaseModel):
    id: UUID
    email: str
    name: str | None
    voice_id: str

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    name: str | None = None
    voice_id: str | None = None
    preferences: dict | None = None
