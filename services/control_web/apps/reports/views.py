"""Представления отчетов."""

import csv

from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.access import report_access_required
from apps.reports.forms import DetailReportFilterForm
from apps.reports.services import (
    build_detail_queryset,
    build_xlsx_response,
    calculate_totals,
    detail_export_rows,
    ensure_export_limit,
)


@report_access_required
def index(_request: HttpRequest) -> HttpResponse:
    """Показать временную страницу раздела отчетов."""

    return HttpResponse("INDCTRL reports")


@report_access_required
def details(request: HttpRequest) -> HttpResponse:
    """Показать HTML-отчет по произведенным деталям."""

    form = DetailReportFilterForm(request.GET or None)
    queryset = build_detail_queryset(form.cleaned_data if form.is_valid() else {})
    totals = calculate_totals(queryset)
    paginator = Paginator(queryset, 50)
    page_obj = paginator.get_page(request.GET.get("page"))
    query_params = request.GET.copy()
    query_params.pop("page", None)

    return render(
        request,
        "reports/details.html",
        {
            "form": form,
            "page_obj": page_obj,
            "query_string": query_params.urlencode(),
            "totals": totals,
        },
    )


@report_access_required
def details_export_csv(request: HttpRequest) -> HttpResponse:
    """Экспортировать отчет деталей в CSV с учетом текущих фильтров."""

    form = DetailReportFilterForm(request.GET or None)
    queryset = build_detail_queryset(form.cleaned_data if form.is_valid() else {})
    try:
        ensure_export_limit(queryset)
    except ValueError as exc:
        return HttpResponse(str(exc), status=400)

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="details.csv"'
    response.write("\ufeff")
    writer = csv.writer(response)
    writer.writerow(
        ["Время события", "Работник", "Станок", "Смена", "Номер детали", "Тип детали", "Состояние"]
    )
    for row in detail_export_rows(queryset):
        writer.writerow(row)
    return response


@report_access_required
def details_export_xlsx(request: HttpRequest) -> HttpResponse:
    """Экспортировать отчет деталей в XLSX с учетом текущих фильтров."""

    form = DetailReportFilterForm(request.GET or None)
    queryset = build_detail_queryset(form.cleaned_data if form.is_valid() else {})
    try:
        ensure_export_limit(queryset)
    except ValueError as exc:
        return HttpResponse(str(exc), status=400)

    return build_xlsx_response(queryset, calculate_totals(queryset))
