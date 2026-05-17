"""Схемы ответов auth-service."""

from uuid import UUID

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Ответ health endpoint'а."""

    status: str
    service: str


class WorkerItem(BaseModel):
    """Краткое описание работника для выбора на ESP32."""

    userID: int
    fullName: str


class DeviceWorkersResponse(BaseModel):
    """Ответ со списком работников, доступных на станке."""

    success: bool
    machineID: int
    machineName: str
    workers: list[WorkerItem]


class LoginResponse(BaseModel):
    """Ответ успешного входа работника."""

    success: bool
    sessionID: UUID
    userID: int
    machineID: int
    workID: int


class StatusResponse(BaseModel):
    """Ответ простой успешной операции."""

    success: bool
    status: str


class ErrorResponse(BaseModel):
    """Единый ответ на прикладную ошибку."""

    success: bool
    error: str
