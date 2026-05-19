"""Сервисный слой dashboard."""

from dataclasses import dataclass

from django.conf import settings
from django.db.models import Count
from django.utils import timezone

from apps.accounts.models import User
from apps.constants import WORK_STATUS_ACTIVE
from apps.machines.models import Device, Machine
from apps.production.models import Detail, InvalidEvent, Work


@dataclass(frozen=True)
class CurrentWorkerRow:
    """Строка dashboard с текущей работой станка."""

    machine_name: str
    worker_name: str
    started_at: object
    last_seen_at: object
    connection_status: str
    connection_label: str


@dataclass(frozen=True)
class DashboardSummary:
    """Краткие показатели для главной страницы."""

    active_works: int
    stale_works: int
    details_today: int
    invalid_events_today: int
    machines_total: int
    devices_total: int
    users_total: int
    recent_details: list


def get_connection_status(last_seen_at, now) -> tuple[str, str]:
    """Определить статус связи по времени последнего heartbeat.

    Если heartbeat свежий, ESP32 считается на связи. Если он старше
    `HEARTBEAT_MAX_AGE_SECONDS`, связь считается устаревшей. Пустое значение означает,
    что после login heartbeat еще не приходил.
    """

    if last_seen_at is None:
        return "no-heartbeat", "heartbeat еще не приходил"

    max_age_seconds = getattr(settings, "HEARTBEAT_MAX_AGE_SECONDS", 180)
    age_seconds = (now - last_seen_at).total_seconds()
    if age_seconds <= max_age_seconds:
        return "alive", "связь активна"
    return "stale", "связь устарела"


def get_dashboard_summary() -> DashboardSummary:
    """Собрать простую агрегацию для главной страницы.

    Dashboard считается на стороне БД короткими запросами, чтобы главная страница
    оставалась быстрой даже при росте таблицы деталей.
    """

    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    active_works = Work.objects.filter(status=WORK_STATUS_ACTIVE).only("last_seen_at")
    stale_works = 0
    for work in active_works:
        status, _label = get_connection_status(work.last_seen_at, now)
        if status in {"stale", "no-heartbeat"}:
            stale_works += 1

    recent_details = list(
        Detail.objects.select_related("user", "machine", "detail_type")
        .order_by("-event_time", "-id")[:8]
    )

    return DashboardSummary(
        active_works=active_works.count(),
        stale_works=stale_works,
        details_today=Detail.objects.filter(event_time__gte=today_start).count(),
        invalid_events_today=InvalidEvent.objects.filter(received_at__gte=today_start).count(),
        machines_total=Machine.objects.aggregate(count=Count("id"))["count"],
        devices_total=Device.objects.aggregate(count=Count("id"))["count"],
        users_total=User.objects.aggregate(count=Count("id"))["count"],
        recent_details=recent_details,
    )


def get_current_workers() -> list[CurrentWorkerRow]:
    """Вернуть активные смены для dashboard текущей работы станков."""

    now = timezone.now()
    works = (
        Work.objects.filter(status=WORK_STATUS_ACTIVE)
        .select_related("user", "machine")
        .order_by("machine__name", "started_at")
    )

    rows = []
    for work in works:
        status, label = get_connection_status(work.last_seen_at, now)
        rows.append(
            CurrentWorkerRow(
                machine_name=work.machine.name,
                worker_name=str(work.user),
                started_at=work.started_at,
                last_seen_at=work.last_seen_at,
                connection_status=status,
                connection_label=label,
            )
        )
    return rows
