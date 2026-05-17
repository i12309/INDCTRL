"""Общие исключения проекта."""


class AppError(Exception):
    """Базовая ошибка приложения с сообщением, понятным для журналов и API."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class DeviceNotFoundError(AppError):
    """ESP32-устройство не найдено по MAC-адресу."""


class UserNotAllowedError(AppError):
    """Пользователю запрещено работать на выбранном станке."""


class ScheduleDeniedError(AppError):
    """Текущее серверное время не входит в разрешенное расписание."""


class MachineBusyError(AppError):
    """Станок уже занят другой активной сменой."""


class SessionNotFoundError(AppError):
    """Сессия авторизации не найдена или больше не активна."""


class ValidationError(AppError):
    """Входящие данные не прошли прикладную проверку."""
