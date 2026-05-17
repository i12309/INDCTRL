# control_common

`control_common` - общий Python-пакет INDCTRL. Он устанавливается в Docker-образы
`auth-service`, `event-service` и `control-web`, чтобы сервисы использовали одни и те
же настройки, константы и helpers.

## Модули

- `config.py` - загрузка переменных окружения через `pydantic-settings` и сборка DSN
  PostgreSQL.
- `db.py` - общий `psycopg_pool.ConnectionPool` для FastAPI-сервисов.
- `constants.py` - роли, статусы смен, состояния деталей и имена сервисов.
- `security.py` - проверка Django password hash без запуска Django ORM.
- `time_utils.py` - текущее серверное время, парсинг времени ESP32 и проверка
  расписания.
- `logging.py` - JSON-логирование в stdout для Docker.
- `responses.py` - единый формат успешных ответов, дублей и ошибок.
- `errors.py` - общие прикладные исключения.

## Установка в Docker

Каждый Dockerfile копирует каталог `common` и устанавливает пакет:

```dockerfile
COPY common ./common
RUN python -m pip install ./common
```

## Почему нельзя дублировать helpers

FastAPI-сервисы и Django работают с одной предметной областью: пользователи, роли,
смены, состояния деталей и PostgreSQL. Если копировать строки статусов, проверку
паролей или парсинг времени в разные сервисы, поведение начнет расходиться. Общий
пакет делает эти правила одним источником правды для всего проекта.
