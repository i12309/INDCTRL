"""Общие исключения проекта."""


class AppError(Exception):
    """Базовая ошибка приложения с сообщением, понятным для журналов и API."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
