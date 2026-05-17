"""Тесты бизнес-логики event-service без реальной PostgreSQL-БД."""

import sys
from datetime import datetime
from pathlib import Path
from uuid import UUID

import pytest

SERVICE_PATH = Path(__file__).resolve().parents[2] / "services" / "event_service"
sys.path.insert(0, str(SERVICE_PATH))
for module_name in list(sys.modules):
    if module_name == "app" or module_name.startswith("app."):
        del sys.modules[module_name]

from app.services.event_service import EventService
from control_common.errors import SessionNotFoundError, ValidationError


FIXED_NOW = datetime(2026, 5, 18, 10, 30)
SESSION_ID = UUID("11111111-1111-1111-1111-111111111111")


class FakeEventRepository:
    """In-memory репозиторий для проверки обработки событий без SQL."""

    def __init__(self) -> None:
        self.session = {
            "session_id": SESSION_ID,
            "user_id": 123,
            "machine_id": 321,
            "work_id": 111,
            "session_is_active": True,
            "work_status": "active",
        }
        self.detail_type = {"id": 2, "code": "bearing", "name": "Подшипник"}
        self.detail_state = {"id": 1, "code": "working", "name": "рабочая"}
        self.next_save_status = "saved"
        self.saved_detail = None
        self.invalid_events = []
        self.last_seen_at = None

    def get_active_session(self, session_id: UUID, _now: datetime) -> dict | None:
        """Вернуть активную сессию по UUID."""

        if self.session and session_id == self.session["session_id"]:
            return self.session
        return None

    def get_active_detail_type(self, detail_type_id: int) -> dict | None:
        """Вернуть активный тип детали."""

        if self.detail_type and detail_type_id == self.detail_type["id"]:
            return self.detail_type
        return None

    def get_active_detail_state(self, detail_state_id: int) -> dict | None:
        """Вернуть активное состояние детали."""

        if self.detail_state and detail_state_id == self.detail_state["id"]:
            return self.detail_state
        return None

    def save_detail_idempotent(self, **kwargs) -> str:
        """Запомнить деталь и вернуть настроенный статус сохранения."""

        self.saved_detail = kwargs
        self.last_seen_at = kwargs["now"]
        return self.next_save_status

    def save_invalid_event(self, **kwargs) -> None:
        """Запомнить некорректное событие."""

        self.invalid_events.append(kwargs)


@pytest.fixture
def repo() -> FakeEventRepository:
    """Создать fake repository для теста."""

    return FakeEventRepository()


@pytest.fixture
def service(repo: FakeEventRepository) -> EventService:
    """Создать EventService с фиксированным временем."""

    return EventService(repository=repo, now_provider=lambda: FIXED_NOW)


def event_body(**overrides) -> bytes:
    """Собрать JSON события детали для теста."""

    payload = {
        "sessionID": str(SESSION_ID),
        "time": "2026-05-16 20:30:00",
        "detail": {"number": 1, "type": 2, "state": 1},
    }
    payload.update(overrides)
    import json

    return json.dumps(payload).encode("utf-8")


def test_successful_detail_save(service: EventService, repo: FakeEventRepository) -> None:
    """Корректное событие сохраняет деталь и возвращает saved."""

    response = service.handle_raw_detail_event(event_body(), source_ip="127.0.0.1")

    assert response.success is True
    assert response.status == "saved"
    assert repo.saved_detail["user_id"] == 123
    assert repo.saved_detail["machine_id"] == 321
    assert repo.saved_detail["work_id"] == 111


def test_duplicate_detail_returns_duplicate(
    service: EventService,
    repo: FakeEventRepository,
) -> None:
    """Повтор того же события не считается ошибкой для ESP32."""

    repo.next_save_status = "duplicate"

    response = service.handle_raw_detail_event(event_body(), source_ip="127.0.0.1")

    assert response.success is True
    assert response.status == "duplicate"


def test_broken_json_is_saved_to_invalid_event(
    service: EventService,
    repo: FakeEventRepository,
) -> None:
    """Битый JSON сохраняется в InvalidEvent."""

    with pytest.raises(ValidationError, match="JSON"):
        service.handle_raw_detail_event(b"{not-json", source_ip="127.0.0.1")

    assert repo.invalid_events[0]["error_text"] == "Некорректный JSON"


def test_unknown_session_is_saved_to_invalid_event(
    service: EventService,
    repo: FakeEventRepository,
) -> None:
    """Неизвестная сессия отклоняет событие и сохраняет InvalidEvent."""

    repo.session = None

    with pytest.raises(SessionNotFoundError):
        service.handle_raw_detail_event(event_body(), source_ip="127.0.0.1")

    assert repo.saved_detail is None
    assert "сессия" in repo.invalid_events[0]["error_text"]


def test_inactive_session_does_not_save_detail(
    service: EventService,
    repo: FakeEventRepository,
) -> None:
    """Неактивная сессия не позволяет сохранить деталь."""

    repo.session = None

    with pytest.raises(SessionNotFoundError):
        service.handle_raw_detail_event(event_body(), source_ip="127.0.0.1")

    assert repo.saved_detail is None


def test_unknown_detail_type_is_error(
    service: EventService,
    repo: FakeEventRepository,
) -> None:
    """Неизвестный тип детали сохраняется как InvalidEvent."""

    repo.detail_type = None

    with pytest.raises(ValidationError, match="Тип детали"):
        service.handle_raw_detail_event(event_body(), source_ip="127.0.0.1")

    assert "Тип детали" in repo.invalid_events[0]["error_text"]


def test_unknown_detail_state_is_error(
    service: EventService,
    repo: FakeEventRepository,
) -> None:
    """Неизвестное состояние детали сохраняется как InvalidEvent."""

    repo.detail_state = None

    with pytest.raises(ValidationError, match="Состояние детали"):
        service.handle_raw_detail_event(event_body(), source_ip="127.0.0.1")

    assert "Состояние детали" in repo.invalid_events[0]["error_text"]


def test_successful_event_updates_work_last_seen_at(
    service: EventService,
    repo: FakeEventRepository,
) -> None:
    """После успешного события обновляется активность смены."""

    service.handle_raw_detail_event(event_body(), source_ip="127.0.0.1")

    assert repo.last_seen_at == FIXED_NOW


def test_mismatched_machine_id_is_saved_to_invalid_event(
    service: EventService,
    repo: FakeEventRepository,
) -> None:
    """Несовпадение machineID с сессией отклоняет событие."""

    with pytest.raises(ValidationError, match="machineID"):
        service.handle_raw_detail_event(event_body(machineID=999), source_ip="127.0.0.1")

    assert "machineID" in repo.invalid_events[0]["error_text"]
