"""Схемы ответов event-service."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Ответ health endpoint'а."""

    status: str
    service: str
