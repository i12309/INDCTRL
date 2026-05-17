"""Бизнес-сервис обработки производственных событий."""

from app.schemas.responses import HealthResponse
from control_common.constants import SERVICE_EVENT
from control_common.responses import health_response


class EventService:
    """Сервис приема и обработки событий от ESP32-терминалов."""

    def health(self) -> HealthResponse:
        """Вернуть состояние процесса без проверки бизнес-зависимостей."""

        return HealthResponse(**health_response(SERVICE_EVENT))
