"""Единые структуры ответов для FastAPI-сервисов."""

from control_common.constants import DEFAULT_HEALTH_STATUS


def health_response(service: str) -> dict[str, str]:
    """Сформировать стандартный ответ health endpoint'а."""

    return {"status": DEFAULT_HEALTH_STATUS, "service": service}


def success_response(status: str) -> dict[str, bool | str]:
    """Сформировать успешный ответ с бизнес-статусом операции."""

    return {"success": True, "status": status}


def saved_response() -> dict[str, bool | str]:
    """Сформировать ответ об успешном сохранении события."""

    return success_response("saved")


def duplicate_response() -> dict[str, bool | str]:
    """Сформировать ответ о повторном событии, которое уже было обработано."""

    return success_response("duplicate")


def error_response(error: str) -> dict[str, bool | str]:
    """Сформировать единый ответ об ошибке обработки запроса."""

    return {"success": False, "error": error}
