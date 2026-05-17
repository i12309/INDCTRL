"""Представления dashboard."""

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

from apps.access import can_view_reports, report_access_required
from apps.dashboard.forms import RoleLoginForm
from apps.dashboard.services import get_current_workers, get_dashboard_summary


class RoleLoginView(LoginView):
    """Панель авторизации с выбором роли пользователя."""

    authentication_form = RoleLoginForm
    template_name = "registration/login.html"
    redirect_authenticated_user = True


@login_required
@require_GET
def index(request: HttpRequest) -> HttpResponse:
    """Показать главную страницу единого интерфейса."""

    summary = get_dashboard_summary() if can_view_reports(request.user) else None
    return render(
        request,
        "dashboard/index.html",
        {
            "summary": summary,
            "page_title": "Главная",
        },
    )


def root(request: HttpRequest) -> HttpResponse:
    """Открыть главный интерфейс или панель входа."""

    if not request.user.is_authenticated:
        return redirect("login")
    return redirect("dashboard:index")


@report_access_required
def current_workers(request: HttpRequest) -> HttpResponse:
    """Показать активные смены и состояние связи ESP32."""

    return render(
        request,
        "dashboard/current_workers.html",
        {
            "rows": get_current_workers(),
            "page_title": "Текущие смены",
        },
    )
