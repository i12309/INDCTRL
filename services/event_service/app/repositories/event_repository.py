"""SQL-доступ event-service к общей PostgreSQL-БД."""

from datetime import datetime
from uuid import UUID

from control_common.constants import SERVICE_EVENT, WORK_STATUS_ACTIVE
from control_common.db import get_connection


class EventRepository:
    """Репозиторий SQL-запросов для приема производственных событий.

    Таблицы созданы Django-миграциями `control-web`; event-service только читает и
    записывает данные через SQL и не управляет схемой БД.
    """

    def get_active_session(self, session_id: UUID, now: datetime) -> dict | None:
        """Найти активную неистекшую сессию и связанную активную смену."""

        with get_connection() as connection:
            return connection.execute(
                """
                SELECT
                    s.id AS session_id,
                    s.user_id,
                    s.machine_id,
                    s.work_id,
                    s.is_active AS session_is_active,
                    s.expires_at,
                    w.status AS work_status
                FROM production_authsession s
                JOIN production_work w ON w.id = s.work_id
                WHERE s.id = %s
                  AND s.is_active = true
                  AND s.expires_at > %s
                  AND w.status = %s
                """,
                (session_id, now, WORK_STATUS_ACTIVE),
            ).fetchone()

    def get_active_detail_type(self, detail_type_id: int) -> dict | None:
        """Найти активный тип детали по ID."""

        with get_connection() as connection:
            return connection.execute(
                """
                SELECT id, code, name
                FROM production_detailtype
                WHERE id = %s
                  AND is_active = true
                """,
                (detail_type_id,),
            ).fetchone()

    def get_active_detail_state(self, detail_state_id: int) -> dict | None:
        """Найти активное состояние детали по ID."""

        with get_connection() as connection:
            return connection.execute(
                """
                SELECT id, code, name
                FROM production_detailstate
                WHERE id = %s
                  AND is_active = true
                """,
                (detail_state_id,),
            ).fetchone()

    def save_detail_idempotent(
        self,
        *,
        user_id: int,
        machine_id: int,
        work_id: int,
        detail_number: int,
        detail_type_id: int,
        detail_state_id: int,
        event_time: datetime,
        now: datetime,
    ) -> str:
        """Сохранить деталь идемпотентно и обновить активность смены.

        `ON CONFLICT DO NOTHING` использует уникальное ограничение Django-модели
        `Detail`. Если ESP32 повторит то же событие, БД не создаст дубль, а сервис
        вернет `duplicate`, чтобы устройство прекратило повторную отправку.
        """

        with get_connection() as connection:
            with connection.transaction():
                inserted = connection.execute(
                    """
                    INSERT INTO production_detail (
                        user_id,
                        machine_id,
                        work_id,
                        detail_number,
                        detail_type_id,
                        detail_state_id,
                        event_time,
                        created_at,
                        updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id, machine_id, work_id, detail_number)
                    DO NOTHING
                    RETURNING id
                    """,
                    (
                        user_id,
                        machine_id,
                        work_id,
                        detail_number,
                        detail_type_id,
                        detail_state_id,
                        event_time,
                        now,
                        now,
                    ),
                ).fetchone()

                connection.execute(
                    """
                    UPDATE production_work
                    SET last_seen_at = %s,
                        updated_at = %s
                    WHERE id = %s
                    """,
                    (now, now, work_id),
                )

        return "saved" if inserted is not None else "duplicate"

    def save_invalid_event(
        self,
        *,
        raw_body: str,
        error_text: str,
        received_at: datetime,
        source_ip: str | None = None,
    ) -> None:
        """Сохранить некорректное входящее событие для диагностики."""

        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO production_invalidevent (
                    received_at,
                    source_ip,
                    raw_body,
                    error_text,
                    service_name,
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (received_at, source_ip, raw_body, error_text, SERVICE_EVENT, received_at),
            )
