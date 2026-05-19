"""Общие проверки доступа для страниц INDCTRL."""

from collections.abc import Callable

from django.contrib.auth.decorators import login_required, user_passes_test

from apps.constants import PERM_VIEW_REPORTS


def can_view_admin(user) -> bool:
    """Проверить базовый доступ к Django admin."""

    return user.is_authenticated and user.is_active and user.is_staff


def can_view_reports(user) -> bool:
    """Проверить доступ к dashboard и отчетам.

    Работники не должны видеть отчеты и текущую занятость станков. Эти страницы
    предназначены только для пользователей с конкретным правом отчетов.
    """

    if not user.is_authenticated or not user.is_active:
        return False
    if user.is_superuser:
        return True

    return user.has_perm(PERM_VIEW_REPORTS)


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
    """Ограничить view пользователями, которым разрешены отчеты."""

    return login_required(user_passes_test(can_view_reports)(view_func))
