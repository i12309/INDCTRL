"""Настройка доступа и заголовков Django admin."""

from django.contrib import admin

from apps.access import can_view_admin


def configure_admin_site() -> None:
    """Применить настройки доступа и человекочитаемые заголовки admin."""

    def site_has_permission(request) -> bool:
        """Ограничить доступ к admin на уровне AdminSite."""

        return can_view_admin(request.user)

    admin.site.has_permission = site_has_permission
    admin.site.site_header = "INDCTRL admin"
    admin.site.site_title = "INDCTRL admin"
    admin.site.index_title = "Управление INDCTRL"
