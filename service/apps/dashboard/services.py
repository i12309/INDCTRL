"""Сервисный слой dashboard."""

from dataclasses import dataclass

from django.conf import settings
from django.utils import timezone

from apps.constants import WORK_STATUS_ACTIVE
from apps.production.models import Work


@dataclass(frozen=True)
class CurrentWorkerRow:
    """Строка dashboard с текущей работой станка."""

    machine_name: str
    worker_name: str
    started_at: object
    last_seen_at: object
    connection_status: str
    connection_label: str


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
