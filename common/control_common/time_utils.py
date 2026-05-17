"""Функции для единообразной работы со временем и расписаниями."""

from datetime import UTC, datetime, time
from zoneinfo import ZoneInfo

from control_common.config import get_settings
from control_common.errors import ValidationError


def utc_now() -> datetime:
    """Вернуть текущий момент времени в UTC."""

    return datetime.now(tz=UTC)


def get_now() -> datetime:
    """Вернуть текущее серверное время в часовом поясе из настроек."""

    timezone_name = get_settings().app_timezone
    return datetime.now(tz=ZoneInfo(timezone_name))


def parse_esp32_datetime(value: str) -> datetime:
    """Разобрать время события ESP32 в формате `YYYY-mm-dd HH:mm:ss`.

    ESP32 присылает локальное время события без timezone. Если формат неверный,
    вызывающий код получает понятную прикладную ошибку для API-ответа и логов.
    """

    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError as exc:
        raise ValidationError("Время события должно быть в формате YYYY-mm-dd HH:mm:ss") from exc


def is_time_inside_schedule(now: datetime, weekday: int, time_from: time, time_to: time) -> bool:
    """Проверить, входит ли серверное время в расписание работы.

    В первой версии смена не пересекает полночь. Если `time_from` больше `time_to`,
    расписание считается ошибочным и должно быть исправлено в админке.
    """

    if weekday < 1 or weekday > 7:
        raise ValidationError("День недели должен быть числом от 1 до 7")
    if time_from > time_to:
        raise ValidationError("Расписание не должно пересекать полночь")

    return now.isoweekday() == weekday and time_from <= now.time() <= time_to
