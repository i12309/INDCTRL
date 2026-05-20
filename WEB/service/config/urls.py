"""URL-маршруты INDCTRL."""

from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.http import JsonResponse
from django.urls import include, path

from apps.api import views as api_views
from apps.constants import DEFAULT_HEALTH_STATUS, SERVICE_INDCTRL
from apps.dashboard.views import IndctrlLoginView, root
from config.admin_site import configure_admin_site

configure_admin_site()


def health(_request):
    """Вернуть состояние Django-сервиса."""

    return JsonResponse({"status": DEFAULT_HEALTH_STATUS, "service": SERVICE_INDCTRL})


urlpatterns = [
    path("", root, name="home"),
    path("login/pin", api_views.device_login, name="device_login_pin"),
    path("login/", IndctrlLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("admin/", admin.site.urls),
    path("api/", include("apps.api.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("reports/", include("apps.reports.urls")),
    path("health/", health, name="health"),
]
