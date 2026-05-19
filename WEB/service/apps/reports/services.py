"""Сервисный слой отчетов."""

from dataclasses import dataclass
from datetime import datetime, time

from django.db.models import Avg, Count, Max, Min, QuerySet
from django.http import HttpResponse
from django.utils import timezone
from openpyxl import Workbook

from apps.production.models import Detail

EXPORT_LIMIT = 50_000
EXPORT_QUERY_CHUNK_SIZE = 1000


@dataclass(frozen=True)
class DetailReportTotals:
    """Итоги отчета по деталям."""

    total: int
    avg_quality: float | None
    min_quality: int | None
    max_quality: int | None


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
    if filters.get("quality_min") is not None:
        queryset = queryset.filter(quality_percent__gte=filters["quality_min"])
    if filters.get("quality_max") is not None:
        queryset = queryset.filter(quality_percent__lte=filters["quality_max"])

    return queryset


def calculate_totals(queryset: QuerySet) -> DetailReportTotals:
    """Рассчитать итоги отчета на стороне БД.

    Агрегация считается на стороне БД, без загрузки всех деталей в память
    Django-процесса.
    """

    totals = queryset.aggregate(
        total=Count("id"),
        avg_quality=Avg("quality_percent"),
        min_quality=Min("quality_percent"),
        max_quality=Max("quality_percent"),
    )
    return DetailReportTotals(
        total=totals["total"],
        avg_quality=totals["avg_quality"],
        min_quality=totals["min_quality"],
        max_quality=totals["max_quality"],
    )


def ensure_export_limit(queryset: QuerySet) -> None:
    """Защитить первую версию экспорта от слишком больших файлов."""

    if queryset.count() > EXPORT_LIMIT:
        raise ValueError(f"Экспорт ограничен {EXPORT_LIMIT} строками")


def detail_export_rows(queryset: QuerySet):
    """Вернуть строки отчета для CSV/XLSX."""

    for detail in queryset.order_by("event_time", "id").iterator(chunk_size=EXPORT_QUERY_CHUNK_SIZE):
        yield [
            detail.event_time.strftime("%Y-%m-%d %H:%M:%S"),
            str(detail.user),
            detail.machine.name,
            detail.work_id,
            detail.detail_number,
            detail.detail_type.name,
            detail.quality_percent,
        ]


def build_xlsx_response(queryset: QuerySet, totals: DetailReportTotals) -> HttpResponse:
    """Сформировать XLSX-файл отчета.

    Excel экспорт нужен менеджерам для дальнейшей ручной обработки. В первой версии
    файл пишется построчно и ограничен `EXPORT_LIMIT` строками.
    """

    workbook = Workbook(write_only=True)
    sheet = workbook.create_sheet(title="Details")
    headers = [
        "Время события",
        "Работник",
        "Станок",
        "Смена",
        "Номер детали",
        "Тип детали",
        "Качество, %",
    ]
    sheet.append(headers)

    for row in detail_export_rows(queryset):
        sheet.append(row)

    sheet.append([])
    sheet.append(["Всего деталей", totals.total])
    sheet.append(["Среднее качество, %", totals.avg_quality])
    sheet.append(["Минимальное качество, %", totals.min_quality])
    sheet.append(["Максимальное качество, %", totals.max_quality])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="details.xlsx"'
    workbook.save(response)
    return response
