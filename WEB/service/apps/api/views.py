"""Простое Django API для ESP32-устройств."""

import json
from datetime import datetime, timedelta
from json import JSONDecodeError
from uuid import UUID

from django.conf import settings
from django.db import IntegrityError, transaction
from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.accounts.models import User
from apps.constants import (
    PERM_USE_ESP32_API,
    SERVICE_INDCTRL,
    WORK_STATUS_ACTIVE,
    WORK_STATUS_FINISHED,
)
from apps.machines.models import Device
from apps.production.models import AuthSession, Detail, DetailType, InvalidEvent, Work
from apps.schedules.models import UserMachineSchedule

# ESP32 не работает как браузер и не хранит Django CSRF cookie, поэтому device API
# освобожден от CSRF. Защита операций строится на пароле работника при login и на
# `sessionID`, который сервер сверяет с активной сменой.


class ApiError(Exception):
    """Прикладная ошибка API с текстом для ESP32 и журналов."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def success_response(status: str) -> JsonResponse:
    """Вернуть успешный ответ с бизнес-статусом."""

    return JsonResponse({"success": True, "status": status})


def error_response(message: str) -> JsonResponse:
    """Вернуть единый ответ API об ошибке."""

    return JsonResponse({"success": False, "error": message})


def _request_json(request: HttpRequest) -> dict:
    """Разобрать JSON body и вернуть словарь верхнего уровня."""

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, JSONDecodeError) as exc:
        raise ApiError("Некорректный JSON") from exc
    if not isinstance(payload, dict):
        raise ApiError("JSON должен быть объектом")
    return payload


def _required(payload: dict, name: str):
    """Получить обязательное поле из JSON."""

    value = payload.get(name)
    if value in (None, ""):
        raise ApiError(f"Поле {name} обязательно")
    return value


def _positive_int(value, field_name: str) -> int:
    """Проверить, что значение является положительным целым числом."""

    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise ApiError(f"Поле {field_name} должно быть числом") from exc
    if result <= 0:
        raise ApiError(f"Поле {field_name} должно быть больше нуля")
    return result


def _int_between(value, field_name: str, min_value: int, max_value: int) -> int:
    """Проверить, что значение является целым числом в заданном диапазоне."""

    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise ApiError(f"Поле {field_name} должно быть числом") from exc
    if result < min_value or result > max_value:
        raise ApiError(f"Поле {field_name} должно быть от {min_value} до {max_value}")
    return result


def _session_uuid(value) -> UUID:
    """Разобрать sessionID в UUID."""

    try:
        return UUID(str(value))
    except ValueError as exc:
        raise ApiError("Поле sessionID должно быть UUID") from exc


def _parse_event_time(value: str) -> datetime:
    """Разобрать локальное время события ESP32."""

    try:
        parsed = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError as exc:
        raise ApiError("Время события должно быть в формате YYYY-mm-dd HH:mm:ss") from exc
    return timezone.make_aware(parsed, timezone.get_current_timezone())


def _schedule_allows_now(schedule: UserMachineSchedule, now: datetime) -> bool:
    """Проверить расписание по текущему серверному времени."""

    local_now = timezone.localtime(now)
    weekday_allowed = schedule.weekday is None or schedule.weekday == local_now.isoweekday()
    time_allowed = (
        schedule.time_from is None
        or schedule.time_to is None
        or schedule.time_from <= local_now.time() <= schedule.time_to
    )
    return weekday_allowed and time_allowed


def _schedule_interval(schedule: UserMachineSchedule, now: datetime) -> tuple[datetime, datetime]:
    """Вернуть границы текущего локального интервала расписания."""

    current_tz = timezone.get_current_timezone()
    local_now = timezone.localtime(now, current_tz)
    if schedule.weekday is None and schedule.time_from is None:
        return (
            datetime.min.replace(tzinfo=current_tz),
            datetime.max.replace(tzinfo=current_tz),
        )

    interval_date = local_now.date()
    if schedule.time_from is None:
        interval_start = timezone.make_aware(datetime.combine(interval_date, datetime.min.time()), current_tz)
        interval_end = timezone.make_aware(datetime.combine(interval_date, datetime.max.time()), current_tz)
        return interval_start, interval_end

    interval_start = timezone.make_aware(datetime.combine(interval_date, schedule.time_from), current_tz)
    interval_end = timezone.make_aware(datetime.combine(interval_date, schedule.time_to), current_tz)
    return interval_start, interval_end


def _get_active_device(mac_address: str) -> Device:
    """Найти активное ESP32-устройство и его станок по MAC-адресу."""

    device = (
        Device.objects.select_related("machine")
        .filter(mac_address__iexact=mac_address.strip())
        .first()
    )
    if device is None:
        raise ApiError("Устройство с таким MAC-адресом не найдено")
    if not device.is_active:
        raise ApiError("ESP32-устройство отключено")
    if not device.machine.is_active:
        raise ApiError("Станок отключен")
    return device


def _user_can_use_esp32_api(user: User) -> bool:
    """Проверить бизнес-право работника на работу через ESP32 API."""

    return user.is_active and user.has_perm(PERM_USE_ESP32_API)


def _user_can_work_now(user: User, machine_id: int, now: datetime) -> bool:
    """Проверить разрешение и активное расписание работника на станке."""

    return bool(_current_work_intervals(user, machine_id, now))


def _current_work_intervals(user: User, machine_id: int, now: datetime) -> list[tuple[datetime, datetime]]:
    """Вернуть интервалы расписания, в которые работник может работать сейчас."""

    schedules = UserMachineSchedule.objects.filter(
        user=user,
        machine_id=machine_id,
        is_active=True,
    )
    return [
        _schedule_interval(schedule, now)
        for schedule in schedules
        if _schedule_allows_now(schedule, now)
    ]


def _work_started_in_current_interval(
    work: Work,
    intervals: list[tuple[datetime, datetime]],
) -> bool:
    """Проверить, относится ли активная смена к текущему интервалу графика."""

    started_at = timezone.localtime(work.started_at)
    return any(interval_start <= started_at <= interval_end for interval_start, interval_end in intervals)


def _deactivate_work_sessions(work: Work) -> None:
    """Отключить старые активные авторизационные сессии смены."""

    AuthSession.objects.filter(work=work, is_active=True).update(is_active=False)


def _get_active_session(session_id: UUID) -> AuthSession:
    """Найти активную неистекшую сессию с активной сменой."""

    session = (
        AuthSession.objects.select_related("user", "machine", "device", "work")
        .filter(
            id=session_id,
            is_active=True,
            expires_at__gt=timezone.now(),
            work__status=WORK_STATUS_ACTIVE,
        )
        .first()
    )
    if session is None:
        raise ApiError("Активная сессия не найдена")
    return session


def _source_ip(request: HttpRequest) -> str | None:
    """Получить IP источника для диагностики InvalidEvent."""

    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip()
    return request.META.get("REMOTE_ADDR")


def _save_invalid_event(request: HttpRequest, message: str) -> None:
    """Сохранить некорректное событие детали вместе с исходным body."""

    InvalidEvent.objects.create(
        source_ip=_source_ip(request),
        raw_body=request.body.decode("utf-8", errors="replace"),
        error_text=message,
        service_name=SERVICE_INDCTRL,
    )


@csrf_exempt
@require_POST
def device_workers(request: HttpRequest) -> JsonResponse:
    """Вернуть работников, доступных для выбранного ESP32-устройства."""

    try:
        payload = _request_json(request)
        device = _get_active_device(str(_required(payload, "macAddress")))
        now = timezone.now()
        workers = []
        for user in User.objects.prefetch_related("groups__permissions", "user_permissions").filter(
            is_active=True,
            machine_schedules__machine=device.machine,
            machine_schedules__is_active=True,
        ).distinct():
            if _user_can_use_esp32_api(user) and _user_can_work_now(user, device.machine_id, now):
                workers.append({"userID": user.id, "fullName": user.full_name})
    except ApiError as exc:
        return error_response(exc.message)

    return JsonResponse(
        {
            "success": True,
            "machineID": device.machine_id,
            "machineName": device.machine.name,
            "workers": workers,
        }
    )


@csrf_exempt
@require_POST
def device_login(request: HttpRequest) -> JsonResponse:
    """Авторизовать работника и создать смену."""

    try:
        payload = _request_json(request)
        user_id = _positive_int(_required(payload, "userID"), "userID")
        password = str(_required(payload, "password"))
        device = _get_active_device(str(_required(payload, "macAddress")))

        user = (
            User.objects.prefetch_related("groups__permissions", "user_permissions")
            .filter(id=user_id, is_active=True)
            .first()
        )
        if user is None or not _user_can_use_esp32_api(user):
            raise ApiError("Пользователь не найден или не является работником")
        if not user.check_password(password):
            raise ApiError("Неверный пароль")

        now = timezone.now()
        work_intervals = _current_work_intervals(user, device.machine_id, now)
        if not work_intervals:
            raise ApiError("Нет разрешения или активного расписания на этот станок")

        expires_at = now + timedelta(minutes=getattr(settings, "SESSION_TTL_MINUTES", 720))
        try:
            with transaction.atomic():
                active_work = (
                    Work.objects.select_for_update()
                    .select_related("user")
                    .filter(machine=device.machine, status=WORK_STATUS_ACTIVE)
                    .first()
                )
                if active_work is not None and active_work.user_id != user.id:
                    raise ApiError(f"Станок занят: {active_work.user.full_name}")

                if active_work is not None and _work_started_in_current_interval(
                    active_work,
                    work_intervals,
                ):
                    work = active_work
                    work.last_seen_at = now
                    work.device = device
                    work.save(update_fields=["last_seen_at", "device", "updated_at"])
                    _deactivate_work_sessions(work)
                else:
                    if active_work is not None:
                        _deactivate_work_sessions(active_work)
                        active_work.status = Work.STATUS_EXPIRED
                        active_work.finished_at = now
                        active_work.save(update_fields=["status", "finished_at", "updated_at"])
                    work = Work.objects.create(
                        user=user,
                        machine=device.machine,
                        device=device,
                        started_at=now,
                        last_seen_at=now,
                        status=WORK_STATUS_ACTIVE,
                    )

                session = AuthSession.objects.create(
                    user=user,
                    machine=device.machine,
                    device=device,
                    work=work,
                    expires_at=expires_at,
                    is_active=True,
                )
        except IntegrityError as exc:
            raise ApiError("Станок уже занят активной сменой") from exc
    except ApiError as exc:
        return error_response(exc.message)

    return JsonResponse(
        {
            "success": True,
            "sessionID": str(session.id),
            "userID": user.id,
            "machineID": device.machine_id,
            "workID": work.id,
        }
    )


@csrf_exempt
@require_POST
def device_heartbeat(request: HttpRequest) -> JsonResponse:
    """Обновить время последней активности смены."""

    try:
        payload = _request_json(request)
        session = _get_active_session(_session_uuid(_required(payload, "sessionID")))
        now = timezone.now()
        session.work.last_seen_at = now
        session.work.save(update_fields=["last_seen_at", "updated_at"])
    except ApiError as exc:
        return error_response(exc.message)

    return success_response("alive")


@csrf_exempt
@require_POST
def device_logout(request: HttpRequest) -> JsonResponse:
    """Закрыть активную сессию и завершить смену."""

    try:
        payload = _request_json(request)
        session = _get_active_session(_session_uuid(_required(payload, "sessionID")))
        now = timezone.now()
        with transaction.atomic():
            session.is_active = False
            session.save(update_fields=["is_active"])
            session.work.status = WORK_STATUS_FINISHED
            session.work.finished_at = now
            session.work.save(update_fields=["status", "finished_at", "updated_at"])
    except ApiError as exc:
        return error_response(exc.message)

    return success_response("finished")


@csrf_exempt
@require_POST
def device_detail(request: HttpRequest) -> JsonResponse:
    """Принять событие произведенной детали."""

    try:
        payload = _request_json(request)
        session = _get_active_session(_session_uuid(_required(payload, "sessionID")))
        detail_payload = _required(payload, "detail")
        if not isinstance(detail_payload, dict):
            raise ApiError("Поле detail должно быть объектом")

        optional_ids = {
            "userID": session.user_id,
            "machineID": session.machine_id,
            "workID": session.work_id,
        }
        for field_name, expected in optional_ids.items():
            if field_name in payload and payload[field_name] is not None:
                if _positive_int(payload[field_name], field_name) != expected:
                    raise ApiError(f"{field_name} не совпадает с активной сессией")

        detail_number = _positive_int(_required(detail_payload, "number"), "detail.number")
        detail_type_id = _positive_int(_required(detail_payload, "type"), "detail.type")
        quality_value = detail_payload.get("quality", detail_payload.get("qualityPercent", detail_payload.get("state")))
        if quality_value in (None, ""):
            raise ApiError("Поле detail.quality обязательно")
        quality_percent = _int_between(quality_value, "detail.quality", 0, 100)
        event_time = _parse_event_time(str(_required(payload, "time")))

        detail_type = DetailType.objects.filter(id=detail_type_id, is_active=True).first()
        if detail_type is None:
            raise ApiError("Тип детали не найден или отключен")

        now = timezone.now()
        with transaction.atomic():
            detail, created = Detail.objects.get_or_create(
                user=session.user,
                machine=session.machine,
                work=session.work,
                detail_number=detail_number,
                defaults={
                    "detail_type": detail_type,
                    "quality_percent": quality_percent,
                    "event_time": event_time,
                },
            )
            session.work.last_seen_at = now
            session.work.save(update_fields=["last_seen_at", "updated_at"])
    except ApiError as exc:
        _save_invalid_event(request, exc.message)
        return error_response(exc.message)

    return success_response("saved" if created else "duplicate")


@csrf_exempt
@require_POST
def device_details(request: HttpRequest) -> JsonResponse:
    """Вернуть детали текущей смены для экрана ESP32 Details."""

    try:
        payload = _request_json(request)
        session = _get_active_session(_session_uuid(_required(payload, "sessionID")))
        details = [
            {
                "number": detail.detail_number,
                "quality": detail.quality_percent,
                "state": f"{detail.quality_percent}%",
                "time": timezone.localtime(detail.event_time).strftime("%Y-%m-%d %H:%M:%S"),
            }
            for detail in Detail.objects.filter(work=session.work)
            .order_by("detail_number", "event_time", "id")
        ]
    except ApiError as exc:
        return error_response(exc.message)

    return JsonResponse({"success": True, "details": details})
