"""Схемы входящих запросов event-service."""

from uuid import UUID

from pydantic import BaseModel, Field


class DetailPayload(BaseModel):
    """Данные произведенной детали от ESP32."""

    number: int = Field(gt=0)
    type: int = Field(gt=0)
    state: int = Field(gt=0)


class DetailEventRequest(BaseModel):
    """Событие о произведенной детали.

    `sessionID` является главным источником user_id, machine_id и work_id. Если ESP32
    дополнительно присылает эти ID, сервис сверяет их с активной сессией.
    """

    session_id: UUID = Field(alias="sessionID")
    time: str
    detail: DetailPayload
    user_id: int | None = Field(default=None, alias="userID", gt=0)
    machine_id: int | None = Field(default=None, alias="machineID", gt=0)
    work_id: int | None = Field(default=None, alias="workID", gt=0)
