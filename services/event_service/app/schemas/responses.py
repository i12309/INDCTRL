"""Схемы ответов event-service."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Ответ health endpoint'а."""

    status: str
    service: str


class StatusResponse(BaseModel):
    """Ответ успешной обработки события."""

    success: bool
    status: str


class ErrorResponse(BaseModel):
    """Единый ответ на ошибку обработки события."""

    success: bool
    error: str
