"""Тесты общих функций времени и расписаний."""

from datetime import datetime, time

import pytest

from control_common.errors import ValidationError
from control_common.time_utils import is_time_inside_schedule, parse_esp32_datetime


def test_parse_esp32_datetime_accepts_expected_format() -> None:
    """ESP32-время в ожидаемом формате преобразуется в datetime."""

    result = parse_esp32_datetime("2026-05-17 14:25:30")

    assert result == datetime(2026, 5, 17, 14, 25, 30)


def test_parse_esp32_datetime_raises_clear_error_for_bad_format() -> None:
    """Неверный формат времени дает понятную прикладную ошибку."""

    with pytest.raises(ValidationError, match="YYYY-mm-dd HH:mm:ss"):
        parse_esp32_datetime("17.05.2026 14:25")


def test_is_time_inside_schedule_returns_true_inside_interval() -> None:
    """Серверное время внутри интервала расписания разрешает работу."""

    now = datetime(2026, 5, 18, 10, 30)

    assert is_time_inside_schedule(now, 1, time(8, 0), time(17, 0)) is True


def test_is_time_inside_schedule_returns_false_for_other_weekday() -> None:
    """Расписание другого дня недели не разрешает работу."""

    now = datetime(2026, 5, 18, 10, 30)

    assert is_time_inside_schedule(now, 2, time(8, 0), time(17, 0)) is False


def test_is_time_inside_schedule_rejects_midnight_crossing() -> None:
    """Пересечение полуночи пока запрещено и должно исправляться в админке."""

    now = datetime(2026, 5, 18, 23, 30)

    with pytest.raises(ValidationError, match="полночь"):
        is_time_inside_schedule(now, 1, time(22, 0), time(6, 0))
