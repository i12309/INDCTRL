"""Бизнес-сервис обработки производственных событий."""

import json
from collections.abc import Callable
from datetime import datetime
from json import JSONDecodeError

from pydantic import ValidationError as PydanticValidationError

from app.repositories.event_repository import EventRepository
from app.schemas.requests import DetailEventRequest
from app.schemas.responses import HealthResponse, StatusResponse
from control_common.constants import SERVICE_EVENT
from control_common.errors import AppError, SessionNotFoundError, ValidationError
from control_common.responses import health_response, saved_response, success_response
from control_common.time_utils import get_now, parse_esp32_datetime


class EventService:
    """Сервис приема и обработки событий от ESP32-терминалов."""

    def __init__(
        self,
        repository: EventRepository | None = None,
        now_provider: Callable[[], datetime] = get_now,
    ) -> None:
        """Создать сервис с репозиторием и источником текущего времени."""

        self.repository = repository or EventRepository()
        self.now_provider = now_provider

    def health(self) -> HealthResponse:
        """Вернуть состояние процесса без проверки бизнес-зависимостей."""

        return HealthResponse(**health_response(SERVICE_EVENT))

    def handle_raw_detail_event(
        self,
        raw_body: bytes,
        *,
        source_ip: str | None,
    ) -> StatusResponse:
        """Принять сырой request body, проверить событие и сохранить деталь.

        Сырой body нужен, чтобы битый JSON или неверную структуру можно было
        сохранить в `InvalidEvent` без потери исходных данных от ESP32.
        """

        received_at = self.now_provider()
        raw_text = raw_body.decode("utf-8", errors="replace")

        try:
            payload = json.loads(raw_text)
        except JSONDecodeError as exc:
            self._save_invalid(raw_text, "Некорректный JSON", received_at, source_ip)
            raise ValidationError("Некорректный JSON") from exc

        try:
            event = DetailEventRequest.model_validate(payload)
        except PydanticValidationError as exc:
            self._save_invalid(raw_text, "Неверная структура события", received_at, source_ip)
            raise ValidationError("Неверная структура события") from exc

        try:
            return self.process_detail_event(event)
        except AppError as exc:
            self._save_invalid(raw_text, exc.message, received_at, source_ip)
            raise

    def process_detail_event(self, event: DetailEventRequest) -> StatusResponse:
        """Проверить событие детали и сохранить его идемпотентно."""

        now = self.now_provider()
        session = self.repository.get_active_session(event.session_id, now)
        if session is None:
            raise SessionNotFoundError("Активная сессия не найдена")

        self._validate_optional_ids(event, session)
        event_time = parse_esp32_datetime(event.time)

        if self.repository.get_active_detail_type(event.detail.type) is None:
            raise ValidationError("Тип детали не найден или отключен")
        if self.repository.get_active_detail_state(event.detail.state) is None:
            raise ValidationError("Состояние детали не найдено или отключено")

        status = self.repository.save_detail_idempotent(
            user_id=session["user_id"],
            machine_id=session["machine_id"],
            work_id=session["work_id"],
            detail_number=event.detail.number,
            detail_type_id=event.detail.type,
            detail_state_id=event.detail.state,
            event_time=event_time,
            now=now,
        )

        if status == "saved":
            return StatusResponse(**saved_response())
        return StatusResponse(**success_response("duplicate"))

    def _validate_optional_ids(self, event: DetailEventRequest, session: dict) -> None:
        """Сверить optional ID из ESP32 с активной сессией.

        Даже если устройство присылает `userID`, `machineID` или `workID`, они не
        считаются источником истины. Несовпадение означает поврежденный или
        подмененный запрос, поэтому событие отклоняется и попадет в `InvalidEvent`.
        """

        if event.user_id is not None and event.user_id != session["user_id"]:
            raise ValidationError("userID не совпадает с активной сессией")
        if event.machine_id is not None and event.machine_id != session["machine_id"]:
            raise ValidationError("machineID не совпадает с активной сессией")
        if event.work_id is not None and event.work_id != session["work_id"]:
            raise ValidationError("workID не совпадает с активной сессией")

    def _save_invalid(
        self,
        raw_body: str,
        error_text: str,
        received_at: datetime,
        source_ip: str | None,
    ) -> None:
        """Сохранить некорректное событие, не скрывая исходную ошибку."""

        self.repository.save_invalid_event(
            raw_body=raw_body,
            error_text=error_text,
            received_at=received_at,
            source_ip=source_ip,
        )
