"""Схемы ответов auth-service."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Ответ health endpoint'а."""

    status: str
    service: str
