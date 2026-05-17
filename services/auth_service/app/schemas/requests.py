"""Схемы входящих запросов auth-service."""

from uuid import UUID

from pydantic import BaseModel, Field


class DeviceWorkersRequest(BaseModel):
    """Запрос списка работников, доступных для ESP32-устройства."""

    mac_address: str = Field(alias="macAddress", min_length=1)


class LoginRequest(BaseModel):
    """Запрос входа работника на станок через ESP32."""

    user_id: int = Field(alias="userID", gt=0)
    password: str = Field(min_length=1)
    mac_address: str = Field(alias="macAddress", min_length=1)


class SessionRequest(BaseModel):
    """Запрос операции по активной сессии работника."""

    session_id: UUID = Field(alias="sessionID")
