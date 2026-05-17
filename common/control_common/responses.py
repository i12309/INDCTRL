"""Единые ответы для служебных endpoint'ов."""

from control_common.constants import DEFAULT_HEALTH_STATUS


def health_response(service: str) -> dict[str, str]:
    """Сформировать стандартный ответ health endpoint'а."""

    return {"status": DEFAULT_HEALTH_STATUS, "service": service}
