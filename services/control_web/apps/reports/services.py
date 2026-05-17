"""Сервисный слой отчетов."""

from dataclasses import dataclass
from datetime import datetime, time

from django.db.models import Count, QuerySet
from django.http import HttpResponse
from django.utils import timezone
from openpyxl import Workbook

from apps.production.models import Detail
from control_common.constants import (
    DETAIL_STATE_DEFECT,
    DETAIL_STATE_UNDEFINED,
    DETAIL_STATE_WORKING,
)

EXPORT_LIMIT = 100_000


@dataclass(frozen=True)
class DetailReportTotals:
    """Итоги отчета по деталям."""

    total: int
    working: int
    defect: int
    undefined: int


def _day_start(value) -> datetime:
    """Преобразовать дату фильтра в начало дня в текущем timezone."""

    return timezone.make_aware(datetime.combine(value, time.min))


def _day_end(value) -> datetime:
    """Преобразовать дату фильтра в конец дня в текущем timezone."""

    return timezone.make_aware(datetime.combine(value, time.max))


def build_detail_queryset(filters: dict) -> QuerySet:
    """Построить QuerySet отчета с фильтрацией на уровне БД.

    `select_related` заранее подтягивает связанные модели, чтобы таблица отчета не
    делала отдельный SQL-запрос для каждой строки.
    """

    queryset = Detail.objects.select_related(
        "user",
        "machine",
        "work",
        "detail_type",
        "detail_state",
    ).order_by("-event_time", "-id")

    if filters.get("date_from"):
        queryset = queryset.filter(event_time__gte=_day_start(filters["date_from"]))
    if filters.get("date_to"):
        queryset = queryset.filter(event_time__lte=_day_end(filters["date_to"]))
    if filters.get("machine"):
        queryset = queryset.filter(machine=filters["machine"])
    if filters.get("user"):
        queryset = queryset.filter(user=filters["user"])
    if filters.get("work"):
        queryset = queryset.filter(work=filters["work"])
    if filters.get("detail_type"):
        queryset = queryset.filter(detail_type=filters["detail_type"])
    if filters.get("detail_state"):
        queryset = queryset.filter(detail_state=filters["detail_state"])

    return queryset


def calculate_totals(queryset: QuerySet) -> DetailReportTotals:
    """Рассчитать итоги отчета на стороне БД.

    Группировка по коду состояния позволяет получить общие цифры без загрузки всех
    деталей в память Django-процесса.
    """

    total = queryset.count()
    by_state = {
        row["detail_state__code"]: row["count"]
        for row in queryset.values("detail_state__code").annotate(count=Count("id"))
    }
    return DetailReportTotals(
        total=total,
        working=by_state.get(DETAIL_STATE_WORKING, 0),
        defect=by_state.get(DETAIL_STATE_DEFECT, 0),
        undefined=by_state.get(DETAIL_STATE_UNDEFINED, 0),
    )


def ensure_export_limit(queryset: QuerySet) -> None:
    """Защитить первую версию экспорта от слишком больших файлов."""

    if queryset.count() > EXPORT_LIMIT:
        raise ValueError(f"Экспорт ограничен {EXPORT_LIMIT} строками")


def detail_export_rows(queryset: QuerySet):
    """Вернуть строки отчета для CSV/XLSX."""

    for detail in queryset.order_by("event_time", "id"):
        yield [
            detail.event_time.strftime("%Y-%m-%d %H:%M:%S"),
            str(detail.user),
            detail.machine.name,
            detail.work_id,
            detail.detail_number,
            detail.detail_type.name,
            detail.detail_state.name,
        ]


def build_xlsx_response(queryset: QuerySet, totals: DetailReportTotals) -> HttpResponse:
    """Сформировать XLSX-файл отчета.

    Excel экспорт нужен менеджерам для дальнейшей ручной обработки. В первой версии
    файл создается целиком в памяти и ограничен `EXPORT_LIMIT` строками.
    """

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Details"
    headers = [
        "Время события",
        "Работник",
        "Станок",
        "Смена",
        "Номер детали",
        "Тип детали",
        "Состояние",
    ]
    sheet.append(headers)

    for row in detail_export_rows(queryset):
        sheet.append(row)

    sheet.append([])
    sheet.append(["Всего деталей", totals.total])
    sheet.append(["Рабочих деталей", totals.working])
    sheet.append(["Брака", totals.defect])
    sheet.append(["Не определено", totals.undefined])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="details.xlsx"'
    workbook.save(response)
    return response
