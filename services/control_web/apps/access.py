"""Общие проверки доступа для страниц control-web."""

from collections.abc import Callable

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ObjectDoesNotExist

from control_common.constants import ROLE_ADMIN, ROLE_DIRECTOR, ROLE_MANAGER

REPORT_ROLES = {ROLE_ADMIN, ROLE_DIRECTOR, ROLE_MANAGER}


def can_view_reports(user) -> bool:
    """Проверить доступ к dashboard и отчетам.

    Работники не должны видеть отчеты и текущую занятость станков. Эти страницы
    предназначены для управленческих ролей: admin, director и manager.
    """

    if not user.is_authenticated or not user.is_active:
        return False
    if user.is_superuser:
        return True

    try:
        role = getattr(user, "role", None)
    except ObjectDoesNotExist:
        return False

    return role is not None and role.code in REPORT_ROLES


def report_access_required(view_func: Callable):
    """Ограничить view ролями, которым разрешены отчеты."""

    return login_required(user_passes_test(can_view_reports)(view_func))
