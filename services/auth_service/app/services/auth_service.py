"""Бизнес-сервис авторизации работников."""

from app.schemas.responses import HealthResponse
from control_common.constants import SERVICE_AUTH
from control_common.responses import health_response
from control_common.security import verify_django_password


class AuthService:
    """Сервис операций авторизации и обслуживания смен."""

    def health(self) -> HealthResponse:
        """Вернуть состояние процесса без проверки бизнес-зависимостей."""

        return HealthResponse(**health_response(SERVICE_AUTH))

    def verify_password(self, raw_password: str, encoded_password: str) -> bool:
        """Проверить пароль работника по Django password hash."""

        return verify_django_password(raw_password, encoded_password)
