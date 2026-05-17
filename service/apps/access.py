"""Общие проверки доступа для страниц INDCTRL."""

from collections.abc import Callable

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ObjectDoesNotExist

from apps.constants import ROLE_ADMIN, ROLE_DIRECTOR, ROLE_MANAGER

REPORT_ROLES = {ROLE_ADMIN, ROLE_DIRECTOR, ROLE_MANAGER}


def can_view_admin(user) -> bool:
    """Проверить доступ к Django admin и справочникам.

    Справочники открываются через стандартный Django admin, поэтому ссылка в
    интерфейсе и серверная проверка admin должны использовать одно правило.
    """

    if not user.is_authenticated or not user.is_active or not user.is_staff:
        return False
    if user.is_superuser:
        return True

    try:
        role = getattr(user, "role", None)
    except ObjectDoesNotExist:
        return False
    return role is not None and role.code == ROLE_ADMIN


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


def ui_access(request) -> dict:
    """Передать в шаблоны доступные разделы единого интерфейса."""

    user = request.user
    return {
        "ui": {
            "can_admin": can_view_admin(user),
            "can_reports": can_view_reports(user),
        }
    }


def report_access_required(view_func: Callable):
    """Ограничить view ролями, которым разрешены отчеты."""

    return login_required(user_passes_test(can_view_reports)(view_func))
