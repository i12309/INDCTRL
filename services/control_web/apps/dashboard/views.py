"""Представления dashboard."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.access import report_access_required
from apps.dashboard.services import get_current_workers


@report_access_required
def index(_request: HttpRequest) -> HttpResponse:
    """Показать временную страницу dashboard."""

    return HttpResponse("INDCTRL dashboard")


@report_access_required
def current_workers(request: HttpRequest) -> HttpResponse:
    """Показать активные смены и состояние связи ESP32."""

    return render(
        request,
        "dashboard/current_workers.html",
        {"rows": get_current_workers()},
    )
