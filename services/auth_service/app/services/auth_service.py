"""Бизнес-сервис авторизации работников."""

from collections.abc import Callable
from datetime import datetime, timedelta

from app.repositories.auth_repository import AuthRepository
from app.schemas.responses import (
    DeviceWorkersResponse,
    HealthResponse,
    LoginResponse,
    StatusResponse,
    WorkerItem,
)
from control_common.config import BaseAppSettings, get_settings
from control_common.constants import ROLE_WORKER, SERVICE_AUTH
from control_common.errors import (
    DeviceNotFoundError,
    MachineBusyError,
    ScheduleDeniedError,
    UserNotAllowedError,
    ValidationError,
)
from control_common.responses import health_response
from control_common.security import verify_django_password
from control_common.time_utils import get_now, is_time_inside_schedule


class AuthService:
    """Сервис операций авторизации и обслуживания смен."""

    def __init__(
        self,
        repository: AuthRepository | None = None,
        now_provider: Callable[[], datetime] = get_now,
        settings: BaseAppSettings | None = None,
    ) -> None:
        """Создать сервис с репозиторием и источником текущего времени."""

        self.repository = repository or AuthRepository()
        self.now_provider = now_provider
        self.settings = settings or get_settings()

    def health(self) -> HealthResponse:
        """Вернуть состояние процесса без проверки бизнес-зависимостей."""

        return HealthResponse(**health_response(SERVICE_AUTH))

    def verify_password(self, raw_password: str, encoded_password: str) -> bool:
        """Проверить пароль работника по Django password hash."""

        return verify_django_password(raw_password, encoded_password)

    def get_workers_for_device(self, mac_address: str) -> DeviceWorkersResponse:
        """Вернуть работников, которые могут работать на станке сейчас."""

        device = self._get_active_device(mac_address)
        now = self.now_provider()
        workers_by_id: dict[int, WorkerItem] = {}

        for row in self.repository.list_worker_schedule_rows(device["machine_id"]):
            if self._schedule_row_allows_now(row, now):
                workers_by_id[row["user_id"]] = WorkerItem(
                    userID=row["user_id"],
                    fullName=row["full_name"],
                )

        return DeviceWorkersResponse(
            success=True,
            machineID=device["machine_id"],
            machineName=device["machine_name"],
            workers=list(workers_by_id.values()),
        )

    def login(self, *, user_id: int, password: str, mac_address: str) -> LoginResponse:
        """Проверить вход работника, создать смену и сессию."""

        device = self._get_active_device(mac_address)
        user = self.repository.get_user_for_login(user_id)
        if user is None or not user["is_active"]:
            raise UserNotAllowedError("Пользователь не найден или отключен")
        if user["role_code"] != ROLE_WORKER:
            raise UserNotAllowedError("Войти на станок может только работник")

        # Пароль не сравнивается с БД напрямую, потому что в БД хранится только hash.
        if not self.verify_password(password, user["password"]):
            raise UserNotAllowedError("Неверный пароль")

        self._check_permission_and_schedule(user_id, device["machine_id"])

        if self.repository.get_active_work_for_machine(device["machine_id"]) is not None:
            raise MachineBusyError("Станок уже занят активной сменой")

        now = self.now_provider()
        expires_at = now + timedelta(minutes=self.settings.session_ttl_minutes)
        session = self.repository.create_work_and_session(
            user_id=user_id,
            machine_id=device["machine_id"],
            device_id=device["device_id"],
            now=now,
            expires_at=expires_at,
        )

        return LoginResponse(
            success=True,
            sessionID=session["session_id"],
            userID=session["user_id"],
            machineID=session["machine_id"],
            workID=session["work_id"],
        )

    def logout(self, session_id) -> StatusResponse:
        """Завершить рабочую смену по активной сессии."""

        self.repository.close_session(session_id, self.now_provider())
        return StatusResponse(success=True, status="finished")

    def heartbeat(self, session_id) -> StatusResponse:
        """Обновить время последнего heartbeat по активной сессии."""

        self.repository.update_heartbeat(session_id, self.now_provider())
        return StatusResponse(success=True, status="alive")

    def _get_active_device(self, mac_address: str) -> dict:
        """Найти активное ESP32-устройство и его активный станок."""

        device = self.repository.get_device_by_mac(mac_address)
        if device is None:
            raise DeviceNotFoundError("Устройство с таким MAC-адресом не найдено")
        if not device["device_is_active"]:
            raise DeviceNotFoundError("ESP32-устройство отключено")
        if not device["machine_is_active"]:
            raise DeviceNotFoundError("Станок отключен")
        return device

    def _check_permission_and_schedule(self, user_id: int, machine_id: int) -> None:
        """Проверить базовое разрешение и текущее расписание работника."""

        if not self.repository.has_machine_permission(user_id, machine_id):
            raise UserNotAllowedError("Нет разрешения работать на этом станке")

        now = self.now_provider()
        schedules = self.repository.list_user_schedule_rows(user_id, machine_id)
        if not schedules:
            raise ScheduleDeniedError("Для работника нет активного расписания на этот станок")
        if not any(self._schedule_row_allows_now(row, now) for row in schedules):
            raise ScheduleDeniedError("Текущее время не входит в расписание работника")

    def _schedule_row_allows_now(self, row: dict, now: datetime) -> bool:
        """Проверить одну строку расписания на текущее серверное время."""

        try:
            return is_time_inside_schedule(now, row["weekday"], row["time_from"], row["time_to"])
        except ValidationError:
            return False
