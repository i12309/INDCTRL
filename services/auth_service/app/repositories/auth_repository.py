"""SQL-доступ auth-service к общей PostgreSQL-БД."""

from datetime import datetime
from uuid import UUID, uuid4

from control_common.constants import ROLE_WORKER, WORK_STATUS_ACTIVE, WORK_STATUS_FINISHED
from control_common.db import get_connection
from control_common.errors import MachineBusyError, SessionNotFoundError


class AuthRepository:
    """Репозиторий SQL-запросов авторизации к таблицам Django.

    FastAPI не управляет миграциями и не использует Django ORM. Он обращается к
    таблицам, созданным миграциями `control-web`, через прямые SQL-запросы.
    """

    def get_device_by_mac(self, mac_address: str) -> dict | None:
        """Найти ESP32-устройство и связанный станок по MAC-адресу."""

        with get_connection() as connection:
            return connection.execute(
                """
                SELECT
                    d.id AS device_id,
                    d.mac_address,
                    d.is_active AS device_is_active,
                    m.id AS machine_id,
                    m.name AS machine_name,
                    m.is_active AS machine_is_active
                FROM machines_device d
                JOIN machines_machine m ON m.id = d.machine_id
                WHERE lower(d.mac_address) = lower(%s)
                """,
                (mac_address.strip(),),
            ).fetchone()

    def list_worker_schedule_rows(self, machine_id: int) -> list[dict]:
        """Вернуть работников с разрешением и расписанием для станка."""

        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    u.id AS user_id,
                    u.full_name,
                    s.weekday,
                    s.time_from,
                    s.time_to
                FROM accounts_user u
                JOIN accounts_role r ON r.id = u.role_id
                JOIN schedules_usermachinepermission p
                    ON p.user_id = u.id AND p.machine_id = %s
                JOIN schedules_usermachineschedule s
                    ON s.user_id = u.id AND s.machine_id = %s
                WHERE u.is_active = true
                  AND r.code = %s
                  AND p.is_allowed = true
                  AND s.is_active = true
                ORDER BY u.full_name, u.id, s.weekday, s.time_from
                """,
                (machine_id, machine_id, ROLE_WORKER),
            ).fetchall()
        return list(rows)

    def get_user_for_login(self, user_id: int) -> dict | None:
        """Получить пользователя и его роль для проверки входа."""

        with get_connection() as connection:
            return connection.execute(
                """
                SELECT
                    u.id AS user_id,
                    u.full_name,
                    u.password,
                    u.is_active,
                    r.code AS role_code
                FROM accounts_user u
                JOIN accounts_role r ON r.id = u.role_id
                WHERE u.id = %s
                """,
                (user_id,),
            ).fetchone()

    def has_machine_permission(self, user_id: int, machine_id: int) -> bool:
        """Проверить базовое разрешение пользователя работать на станке."""

        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM schedules_usermachinepermission
                WHERE user_id = %s
                  AND machine_id = %s
                  AND is_allowed = true
                """,
                (user_id, machine_id),
            ).fetchone()
        return row is not None

    def list_user_schedule_rows(self, user_id: int, machine_id: int) -> list[dict]:
        """Вернуть активные расписания пользователя для конкретного станка."""

        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT weekday, time_from, time_to
                FROM schedules_usermachineschedule
                WHERE user_id = %s
                  AND machine_id = %s
                  AND is_active = true
                ORDER BY weekday, time_from
                """,
                (user_id, machine_id),
            ).fetchall()
        return list(rows)

    def get_active_work_for_machine(self, machine_id: int) -> dict | None:
        """Найти активную смену на станке."""

        with get_connection() as connection:
            return connection.execute(
                """
                SELECT id, user_id, machine_id
                FROM production_work
                WHERE machine_id = %s
                  AND status = %s
                """,
                (machine_id, WORK_STATUS_ACTIVE),
            ).fetchone()

    def create_work_and_session(
        self,
        *,
        user_id: int,
        machine_id: int,
        device_id: int,
        now: datetime,
        expires_at: datetime,
    ) -> dict:
        """Создать рабочую смену и сессию авторизации в одной транзакции."""

        session_id = uuid4()

        try:
            with get_connection() as connection:
                with connection.transaction():
                    active_work = connection.execute(
                        """
                        SELECT id
                        FROM production_work
                        WHERE machine_id = %s
                          AND status = %s
                        """,
                        (machine_id, WORK_STATUS_ACTIVE),
                    ).fetchone()
                    if active_work is not None:
                        raise MachineBusyError("Станок уже занят активной сменой")

                    work = connection.execute(
                        """
                        INSERT INTO production_work (
                            user_id,
                            machine_id,
                            device_id,
                            started_at,
                            last_seen_at,
                            status,
                            created_at,
                            updated_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (
                            user_id,
                            machine_id,
                            device_id,
                            now,
                            now,
                            WORK_STATUS_ACTIVE,
                            now,
                            now,
                        ),
                    ).fetchone()

                    connection.execute(
                        """
                        INSERT INTO production_authsession (
                            id,
                            user_id,
                            machine_id,
                            device_id,
                            work_id,
                            created_at,
                            expires_at,
                            is_active
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, true)
                        """,
                        (
                            session_id,
                            user_id,
                            machine_id,
                            device_id,
                            work["id"],
                            now,
                            expires_at,
                        ),
                    )
        except Exception as exc:
            # Partial unique index в БД защищает от гонки двух одновременных login.
            if getattr(exc, "sqlstate", None) == "23505":
                raise MachineBusyError("Станок уже занят активной сменой") from exc
            raise

        return {
            "session_id": session_id,
            "user_id": user_id,
            "machine_id": machine_id,
            "work_id": work["id"],
        }

    def close_session(self, session_id: UUID, now: datetime) -> None:
        """Закрыть активную сессию и завершить связанную рабочую смену."""

        with get_connection() as connection:
            with connection.transaction():
                session = connection.execute(
                    """
                    SELECT id, work_id
                    FROM production_authsession
                    WHERE id = %s
                      AND is_active = true
                    """,
                    (session_id,),
                ).fetchone()
                if session is None:
                    raise SessionNotFoundError("Активная сессия не найдена")

                connection.execute(
                    """
                    UPDATE production_authsession
                    SET is_active = false
                    WHERE id = %s
                    """,
                    (session_id,),
                )
                connection.execute(
                    """
                    UPDATE production_work
                    SET status = %s,
                        finished_at = %s,
                        updated_at = %s
                    WHERE id = %s
                    """,
                    (WORK_STATUS_FINISHED, now, now, session["work_id"]),
                )

    def update_heartbeat(self, session_id: UUID, now: datetime) -> None:
        """Обновить `last_seen_at` у смены активной сессии."""

        with get_connection() as connection:
            with connection.transaction():
                session = connection.execute(
                    """
                    SELECT id, work_id
                    FROM production_authsession
                    WHERE id = %s
                      AND is_active = true
                      AND expires_at > %s
                    """,
                    (session_id, now),
                ).fetchone()
                if session is None:
                    raise SessionNotFoundError("Активная сессия не найдена")

                connection.execute(
                    """
                    UPDATE production_work
                    SET last_seen_at = %s,
                        updated_at = %s
                    WHERE id = %s
                    """,
                    (now, now, session["work_id"]),
                )
