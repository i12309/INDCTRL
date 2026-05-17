"""Представления dashboard."""

from django.http import HttpRequest, HttpResponse


def index(_request: HttpRequest) -> HttpResponse:
    """Показать временную страницу dashboard."""

    return HttpResponse("INDCTRL dashboard")
