"""Тесты бизнес-логики auth-service без реальной PostgreSQL-БД."""

from datetime import datetime, time
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest

from app.services.auth_service import AuthService
from control_common.errors import (
    DeviceNotFoundError,
    MachineBusyError,
    ScheduleDeniedError,
    UserNotAllowedError,
)


DJANGO_HASH = "pbkdf2_sha256$720000$testsalt$1Gcs0kxgCMnRfX3SeHtQ/XAmc0Vp6UZQGId2xXfmeck="
FIXED_NOW = datetime(2026, 5, 18, 10, 30)


class FakeAuthRepository:
    """In-memory репозиторий для проверки бизнес-логики без SQL."""

    def __init__(self) -> None:
        self.device = {
            "device_id": 10,
            "mac_address": "AA:BB:CC:DD:EE:FF",
            "device_is_active": True,
            "machine_id": 321,
            "machine_name": "Станок №1",
            "machine_is_active": True,
        }
        self.user = {
            "user_id": 123,
            "full_name": "Иванов Иван Иванович",
            "password": DJANGO_HASH,
            "is_active": True,
            "role_code": "worker",
        }
        self.permission_allowed = True
        self.schedule_rows = [{"weekday": 1, "time_from": time(8, 0), "time_to": time(17, 0)}]
        self.active_work = None
        self.created_session_id = UUID("11111111-1111-1111-1111-111111111111")
        self.closed_session_id = None
        self.heartbeat_session_id = None
        self.heartbeat_at = None

    def get_device_by_mac(self, mac_address: str) -> dict | None:
        """Вернуть устройство, если MAC совпадает."""

        if mac_address.lower() == self.device["mac_address"].lower():
            return self.device
        return None

    def list_worker_schedule_rows(self, machine_id: int) -> list[dict]:
        """Вернуть строки работников с расписанием."""

        if machine_id != self.device["machine_id"]:
            return []
        return [
            {
                "user_id": self.user["user_id"],
                "full_name": self.user["full_name"],
                **row,
            }
            for row in self.schedule_rows
        ]

    def get_user_for_login(self, user_id: int) -> dict | None:
        """Вернуть пользователя для login."""

        if user_id == self.user["user_id"]:
            return self.user
        return None

    def has_machine_permission(self, _user_id: int, _machine_id: int) -> bool:
        """Вернуть настройку базового разрешения."""

        return self.permission_allowed

    def list_user_schedule_rows(self, _user_id: int, _machine_id: int) -> list[dict]:
        """Вернуть расписания пользователя."""

        return self.schedule_rows

    def get_active_work_for_machine(self, _machine_id: int) -> dict | None:
        """Вернуть активную смену, если станок занят."""

        return self.active_work

    def create_work_and_session(self, **_kwargs) -> dict:
        """Создать фиктивную смену и сессию."""

        return {
            "session_id": self.created_session_id,
            "user_id": self.user["user_id"],
            "machine_id": self.device["machine_id"],
            "work_id": 111,
        }

    def close_session(self, session_id: UUID, _now: datetime) -> None:
        """Запомнить закрытую сессию."""

        self.closed_session_id = session_id

    def update_heartbeat(self, session_id: UUID, now: datetime) -> None:
        """Запомнить обновленный heartbeat."""

        self.heartbeat_session_id = session_id
        self.heartbeat_at = now


@pytest.fixture
def repo() -> FakeAuthRepository:
    """Создать fake repository для теста."""

    return FakeAuthRepository()


@pytest.fixture
def service(repo: FakeAuthRepository) -> AuthService:
    """Создать AuthService с фиксированным временем."""

    return AuthService(
        repository=repo,
        now_provider=lambda: FIXED_NOW,
        settings=SimpleNamespace(session_ttl_minutes=720),
    )


def test_get_workers_by_mac(service: AuthService) -> None:
    """ESP32 получает список работников по MAC-адресу."""

    response = service.get_workers_for_device("AA:BB:CC:DD:EE:FF")

    assert response.success is True
    assert response.machineID == 321
    assert response.workers[0].userID == 123


def test_get_workers_unknown_mac_returns_error(service: AuthService) -> None:
    """Неизвестный MAC дает прикладную ошибку."""

    with pytest.raises(DeviceNotFoundError):
        service.get_workers_for_device("00:00:00:00:00:00")


def test_successful_login_creates_work_and_session(service: AuthService) -> None:
    """Успешный login возвращает sessionID, userID, machineID и workID."""

    response = service.login(
        user_id=123,
        password="secret",
        mac_address="AA:BB:CC:DD:EE:FF",
    )

    assert response.success is True
    assert response.sessionID == UUID("11111111-1111-1111-1111-111111111111")
    assert response.userID == 123
    assert response.machineID == 321
    assert response.workID == 111


def test_login_rejects_wrong_password(service: AuthService) -> None:
    """Неверный пароль не допускает работника к станку."""

    with pytest.raises(UserNotAllowedError, match="Неверный пароль"):
        service.login(user_id=123, password="wrong", mac_address="AA:BB:CC:DD:EE:FF")


def test_login_rejects_missing_machine_permission(
    service: AuthService,
    repo: FakeAuthRepository,
) -> None:
    """Отсутствие базового разрешения запрещает вход."""

    repo.permission_allowed = False

    with pytest.raises(UserNotAllowedError, match="Нет разрешения"):
        service.login(user_id=123, password="secret", mac_address="AA:BB:CC:DD:EE:FF")


def test_login_rejects_schedule_denied(service: AuthService, repo: FakeAuthRepository) -> None:
    """Если текущее время не попадает в расписание, вход запрещен."""

    repo.schedule_rows = [{"weekday": 2, "time_from": time(8, 0), "time_to": time(17, 0)}]

    with pytest.raises(ScheduleDeniedError, match="расписание"):
        service.login(user_id=123, password="secret", mac_address="AA:BB:CC:DD:EE:FF")


def test_login_rejects_busy_machine(service: AuthService, repo: FakeAuthRepository) -> None:
    """Если станок уже занят активной сменой, новый вход запрещен."""

    repo.active_work = {"id": 777, "machine_id": 321}

    with pytest.raises(MachineBusyError, match="занят"):
        service.login(user_id=123, password="secret", mac_address="AA:BB:CC:DD:EE:FF")


def test_logout_closes_work_and_session(service: AuthService, repo: FakeAuthRepository) -> None:
    """Logout передает репозиторию команду закрыть сессию и смену."""

    session_id = uuid4()
    response = service.logout(session_id)

    assert response.success is True
    assert response.status == "finished"
    assert repo.closed_session_id == session_id


def test_heartbeat_updates_last_seen_at(service: AuthService, repo: FakeAuthRepository) -> None:
    """Heartbeat обновляет время последней активности смены."""

    session_id = uuid4()
    response = service.heartbeat(session_id)

    assert response.success is True
    assert response.status == "alive"
    assert repo.heartbeat_session_id == session_id
    assert repo.heartbeat_at == FIXED_NOW
