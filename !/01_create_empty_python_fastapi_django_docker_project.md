# Задача 01. Создать проект в пустом GitHub-репозитории под Python, FastAPI, Django и Docker

## Цель

Создать базовую структуру проекта для системы контроля работы станков. Проект должен сразу быть рассчитан на запуск через Docker Compose на одном Linux-сервере.

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

## Архитектурное решение

Сделать не четыре web-сервиса, а три прикладных сервиса:

```text
auth-service   FastAPI. Авторизация работников на ESP32, создание смены, heartbeat, logout.
event-service  FastAPI. Прием событий о произведенных деталях от ESP32.
control-web    Django. Админка, dashboard, отчеты, экспорт CSV/XLSX.
```

Причина объединения админки и отчетов в `control-web`:

```text
Django уже содержит admin, ORM, систему авторизации, шаблоны и формы.
Админка и отчеты используют одни и те же модели БД.
Для первой версии не надо дублировать Django-модели, настройки и миграции в двух сервисах.
```

## Технологии

Использовать:

```text
Python 3.12+
FastAPI
Uvicorn
Django 5.2 LTS или актуальную стабильную LTS-версию Django
Gunicorn
PostgreSQL
psycopg 3 / psycopg_pool
Pydantic v2
pydantic-settings
openpyxl для Excel-выгрузок
pytest
ruff
black
Docker
Docker Compose
Nginx
```

Не использовать SQLite для рабочей версии.

## Структура проекта

Создать структуру:

```text
INDCTRL/
  README.md
  .gitignore
  .dockerignore
  .env.example
  docker-compose.yml
  compose.production.yml
  Makefile
  pyproject.toml

  common/
    pyproject.toml
    control_common/
      __init__.py
      config.py
      constants.py
      db.py
      errors.py
      logging.py
      responses.py
      security.py
      time_utils.py

  services/
    auth_service/
      README.md
      requirements.txt
      app/
        __init__.py
        main.py
        api/
          __init__.py
          routes.py
        repositories/
          __init__.py
          auth_repository.py
        schemas/
          __init__.py
          requests.py
          responses.py
        services/
          __init__.py
          auth_service.py

    event_service/
      README.md
      requirements.txt
      app/
        __init__.py
        main.py
        api/
          __init__.py
          routes.py
        repositories/
          __init__.py
          event_repository.py
        schemas/
          __init__.py
          requests.py
          responses.py
        services/
          __init__.py
          event_service.py

    control_web/
      README.md
      requirements.txt
      manage.py
      config/
        __init__.py
        settings.py
        urls.py
        wsgi.py
        asgi.py
      apps/
        accounts/
          __init__.py
          admin.py
          apps.py
          models.py
          migrations/
            __init__.py
        machines/
          __init__.py
          admin.py
          apps.py
          models.py
          migrations/
            __init__.py
        production/
          __init__.py
          admin.py
          apps.py
          models.py
          migrations/
            __init__.py
        schedules/
          __init__.py
          admin.py
          apps.py
          models.py
          migrations/
            __init__.py
        reports/
          __init__.py
          apps.py
          urls.py
          views.py
          services.py
          forms.py
          templates/
            reports/
        dashboard/
          __init__.py
          apps.py
          urls.py
          views.py
          templates/
            dashboard/
      static/
      templates/

  docker/
    auth-service.Dockerfile
    event-service.Dockerfile
    control-web.Dockerfile
    nginx/
      default.conf

  deploy/
    scripts/
      backup_postgres.sh
      restore_postgres.sh
      deploy.sh
      wait_for_postgres.py
    systemd/
      INDCTRL.service.example

  docs/
    architecture.md
    database.md
    docker.md
    env.md
    services/
      auth-service.md
      event-service.md
      control-web.md
    linux/
      install-docker.md
      first-run.md
      update.md
      logs.md
      https.md
    backup/
      postgres-backup.md
      postgres-restore.md

  tests/
    common/
    auth_service/
    event_service/
    control_web/
```

## Docker-файлы в первой задаче

Создать минимальные Dockerfile'ы:

```text
docker/auth-service.Dockerfile
docker/event-service.Dockerfile
docker/control-web.Dockerfile
```

На первом этапе они должны запускать только health endpoint'ы, но структура должна быть production-ready:

- использовать `python:3.12-slim`;
- устанавливать зависимости из `requirements.txt`;
- устанавливать общий пакет `common`;
- не использовать bind-mount исходного кода в production compose;
- задавать `WORKDIR /app`;
- запускать сервисы не от root-пользователя, если это не ломает первый запуск;
- добавить понятные комментарии в Dockerfile там, где действие может быть неочевидно новичку.

## docker-compose.yml

Создать `docker-compose.yml` для локального и базового запуска:

Сервисы:

```text
postgres
auth-service
event-service
control-web
nginx
```

Требования:

- PostgreSQL не публиковать наружу на порт `5432` по умолчанию.
- Наружу публиковать только Nginx: `80:80`.
- Для PostgreSQL использовать volume `postgres_data`.
- Для Django static files использовать volume `static_data`.
- Все сервисы должны быть в одной внутренней Docker-сети.
- У PostgreSQL должен быть `healthcheck`.
- Прикладные сервисы должны зависеть от здорового PostgreSQL.
- Для всех контейнеров указать `restart: unless-stopped`.

## compose.production.yml

Создать отдельный `compose.production.yml`, который:

- не использует bind-mount исходного кода;
- использует только Docker images/build;
- содержит production-настройки;
- подходит для запуска на Linux-сервере предприятия.

## .env.example

Создать `.env.example`:

```env
APP_ENV=local
APP_TIMEZONE=Europe/Berlin

POSTGRES_DB=machine_control
POSTGRES_USER=machine_control
POSTGRES_PASSWORD=change_me_strong_password
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

DJANGO_SECRET_KEY=change_me
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,control.local
DJANGO_CSRF_TRUSTED_ORIGINS=http://127.0.0.1,http://localhost

AUTH_SERVICE_PORT=8000
EVENT_SERVICE_PORT=8000
CONTROL_WEB_PORT=8000

SESSION_TTL_MINUTES=720
HEARTBEAT_MAX_AGE_SECONDS=180
```

Настоящий `.env` не должен попадать в git.

## Минимальные health endpoint'ы

Сразу реализовать:

```http
GET /health
```

для `auth-service` и `event-service`.

Для Django:

```http
GET /health/
```

Ответ:

```json
{"status": "ok", "service": "control-web"}
```

## Makefile

Добавить удобные команды:

```makefile
make build
make up
make down
make logs
make ps
make migrate
make createsuperuser
make collectstatic
make test
make lint
make format
make backup
```

## README.md

В корневом `README.md` описать:

1. назначение проекта;
2. состав сервисов;
3. почему используется PostgreSQL;
4. почему используется Docker Compose;
5. почему админка и отчеты объединены в `control-web`;
6. первый запуск;
7. команды Docker Compose;
8. где находится документация;
9. как смотреть логи;
10. как выполнить миграции;
11. как создать администратора Django.

## Критерии приемки

- Репозиторий можно клонировать и выполнить `cp .env.example .env`.
- Команда `docker compose up -d --build` поднимает все контейнеры.
- `GET /health` для FastAPI-сервисов возвращает `ok`.
- `GET /health/` для Django возвращает `ok`.
- Есть корневой README и README каждого сервиса.
- В проекте нет настоящих паролей, секретов и production `.env`.
