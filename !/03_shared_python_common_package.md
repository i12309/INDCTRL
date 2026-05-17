# Задача 03. Реализовать общий Python-пакет `control_common`

## Цель

Создать общий пакет с настройками, подключением к PostgreSQL, логированием, константами, проверкой паролей и общими helpers для FastAPI-сервисов.

## Общие обязательные требования

- Проект называется `INDCTRL`.
- Язык: Python 3.12+.
- База данных: PostgreSQL.
- Запуск в production: Docker Compose на одном Linux-сервере.
- Сервисы:
  - `auth-service` — FastAPI-сервис авторизации работников на ESP32;
  - `event-service` — FastAPI-сервис приема событий о произведенных деталях;
  - `control-web` — Django-сервис, который содержит админку, dashboard и отчеты;
  - `postgres` — общая PostgreSQL-БД;
  - `nginx` — единая точка входа для HTTP.
- Админка и отчеты должны быть в одном Django-сервисе `control-web`. Внутри Django их надо разделить по приложениям/модулям.
- Django-модели и Django migrations являются основным источником структуры БД.
- FastAPI-сервисы работают с этой же БД напрямую через общий пакет и SQL-запросы, но не запускают миграции.
- Весь код должен быть понятен программисту, который плохо знает Python, FastAPI и Django.
- Все публичные классы, Django-модели, Pydantic-схемы, функции, методы и сервисные классы должны иметь докстринги или комментарии на русском языке.
- Сложная бизнес-логика должна быть пояснена комментариями на русском языке: проверки прав, расписаний, активных смен, идемпотентности, обработки дублей и ошибок.
- Комментарии должны объяснять смысл и причину решения, а не дублировать очевидное действие кода.
- В каждом сервисе должна быть собственная документация `README.md`: назначение, переменные окружения, запуск в Docker, основные endpoint'ы, диагностика и просмотр логов.

## Где находится пакет

```text
common/control_common/
```

Пакет должен устанавливаться в Docker-образах FastAPI и Django.

## Модули

### `config.py`

Реализовать загрузку настроек через `pydantic-settings`.

Настройки:

```text
APP_ENV
APP_TIMEZONE
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_HOST
POSTGRES_PORT
SESSION_TTL_MINUTES
HEARTBEAT_MAX_AGE_SECONDS
```

Добавить helper для формирования DSN PostgreSQL.

### `db.py`

Реализовать подключение к PostgreSQL через `psycopg_pool.ConnectionPool`.

Требования:

- создать функцию инициализации пула;
- создать функцию получения connection;
- добавить закрытие пула при завершении FastAPI-приложения;
- все функции снабдить русскоязычными докстрингами.

FastAPI-сервисы должны использовать этот общий модуль, а не создавать подключение к БД самостоятельно.

### `constants.py`

Описать общие константы:

```text
ROLE_ADMIN = "admin"
ROLE_DIRECTOR = "director"
ROLE_MANAGER = "manager"
ROLE_WORKER = "worker"

WORK_STATUS_ACTIVE = "active"
WORK_STATUS_FINISHED = "finished"
WORK_STATUS_EXPIRED = "expired"
WORK_STATUS_CANCELLED = "cancelled"

DETAIL_STATE_WORKING = "working"
DETAIL_STATE_DEFECT = "defect"
DETAIL_STATE_UNDEFINED = "undefined"
```

### `security.py`

Реализовать проверку пароля работника.

Требование:

- Django хранит пароль в поле `password` кастомной модели пользователя.
- FastAPI `auth-service` должен уметь проверить пароль по этому hash.
- Сделать функцию:

```python
def verify_django_password(raw_password: str, encoded_password: str) -> bool:
    """Проверяет обычный пароль пользователя по hash, сохраненному Django."""
```

Допустимо использовать `django.contrib.auth.hashers.check_password`, но так, чтобы FastAPI-сервису не требовалось запускать Django ORM и миграции.

Рядом в комментарии объяснить, почему пароль нельзя хранить открытым текстом.

### `time_utils.py`

Реализовать helpers:

```text
get_now()
parse_esp32_datetime(value: str)
is_time_inside_schedule(now, weekday, time_from, time_to)
```

Требования:

- входящее время детали приходит от ESP32;
- проверка расписания выполняется по времени сервера;
- формат времени события: `YYYY-mm-dd HH:mm:ss`;
- при ошибке парсинга возвращать понятную ошибку.

### `logging.py`

Настроить структурированное логирование в stdout.

Логи должны быть удобны для просмотра через:

```bash
docker compose logs auth-service
docker compose logs event-service
docker compose logs control-web
```

### `responses.py`

Общие структуры ответов:

```json
{"success": true, "status": "saved"}
{"success": true, "status": "duplicate"}
{"success": false, "error": "..."}
```

### `errors.py`

Описать общие исключения:

```text
DeviceNotFoundError
UserNotAllowedError
ScheduleDeniedError
MachineBusyError
SessionNotFoundError
ValidationError
```

## Документация

Создать `common/README.md`:

- назначение пакета;
- какие модули есть;
- какие сервисы его используют;
- как устанавливается в Dockerfile;
- почему нельзя дублировать общие функции по сервисам.

## Критерии приемки

- FastAPI-сервисы импортируют настройки, DB pool, constants и security helpers из `control_common`.
- Нет дублирования строк ролей и статусов в разных сервисах.
- Все публичные функции имеют русскоязычные докстринги.
- Есть unit-тесты для проверки расписания, парсинга времени и проверки пароля.
