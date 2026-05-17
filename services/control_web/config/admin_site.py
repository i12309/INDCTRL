"""Настройка доступа и заголовков Django admin."""

from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist

from control_common.constants import ROLE_ADMIN


def has_admin_role(user) -> bool:
    """Проверить, что пользователь имеет право входить в `/admin/`.

    Доступ получают активные staff-пользователи с ролью `admin`. Django superuser
    тоже допускается, чтобы штатная команда `createsuperuser` не блокировала вход.
    """

    if not user.is_active or not user.is_staff:
        return False
    if user.is_superuser:
        return True

    try:
        role = getattr(user, "role", None)
    except ObjectDoesNotExist:
        return False
    return role is not None and role.code == ROLE_ADMIN


def configure_admin_site() -> None:
    """Применить настройки доступа и человекочитаемые заголовки admin."""

    def site_has_permission(request) -> bool:
        """Ограничить доступ к admin на уровне AdminSite."""

        return has_admin_role(request.user)

    admin.site.has_permission = site_has_permission
    admin.site.site_header = "INDCTRL admin"
    admin.site.site_title = "INDCTRL admin"
    admin.site.index_title = "Управление INDCTRL"
