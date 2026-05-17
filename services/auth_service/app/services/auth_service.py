"""Бизнес-сервис авторизации работников."""

from app.schemas.responses import HealthResponse
from control_common.constants import SERVICE_AUTH
from control_common.responses import health_response


class AuthService:
    """Сервис операций авторизации и обслуживания смен."""

    def health(self) -> HealthResponse:
        """Вернуть состояние процесса без проверки бизнес-зависимостей."""

        return HealthResponse(**health_response(SERVICE_AUTH))
