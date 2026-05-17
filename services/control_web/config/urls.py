"""URL-маршруты control-web."""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

from control_common.constants import SERVICE_CONTROL_WEB
from control_common.responses import health_response


def health(_request):
    """Вернуть состояние Django-сервиса."""

    return JsonResponse(health_response(SERVICE_CONTROL_WEB))


urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", include("apps.dashboard.urls")),
    path("reports/", include("apps.reports.urls")),
    path("health/", health, name="health"),
]
