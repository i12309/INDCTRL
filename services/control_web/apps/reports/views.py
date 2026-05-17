"""Представления отчетов."""

from django.http import HttpRequest, HttpResponse


def index(_request: HttpRequest) -> HttpResponse:
    """Показать временную страницу раздела отчетов."""

    return HttpResponse("INDCTRL reports")
