# Задача 08. Настроить Docker Compose, production-образы и Nginx

## Цель

Сделать полноценную Docker Compose-конфигурацию для запуска всей системы на одном Linux-сервере в production.

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

## Сервисы Docker Compose

В `docker-compose.yml` и `compose.production.yml` должны быть сервисы:

```text
postgres
auth-service
event-service
control-web
nginx
```

Дополнительно можно подготовить profile/tool-сервис для backup, но основной backup можно делать скриптом.

## PostgreSQL

Требования:

```text
image: postgres:17 или актуальная стабильная версия;
volume postgres_data для /var/lib/postgresql/data;
healthcheck через pg_isready;
не публиковать порт 5432 наружу;
переменные окружения брать из .env.
```

Пример логики:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB"]
  interval: 10s
  timeout: 5s
  retries: 5
```

## FastAPI-сервисы

`auth-service` и `event-service`:

```text
build context: корень проекта;
dockerfile: docker/auth-service.Dockerfile или docker/event-service.Dockerfile;
depends_on postgres condition service_healthy;
restart: unless-stopped;
не публиковать ports наружу;
expose 8000 внутри Docker-сети;
логи писать в stdout.
```

## Django `control-web`

Требования:

```text
build context: корень проекта;
dockerfile: docker/control-web.Dockerfile;
depends_on postgres condition service_healthy;
restart: unless-stopped;
expose 8000;
volume static_data для static files;
логи писать в stdout.
```

Миграции не выполнять автоматически в бесконечном цикле старта контейнера. Подготовить команды:

```bash
docker compose exec control-web python manage.py migrate
docker compose exec control-web python manage.py collectstatic --noinput
docker compose exec control-web python manage.py createsuperuser
```

Можно добавить `deploy/scripts/deploy.sh`, который выполняет эти команды в правильном порядке.

## Nginx

Создать `docker/nginx/default.conf`.

Маршрутизация:

```text
/health-auth/     -> auth-service /health
/health-events/   -> event-service /health
/health-web/      -> control-web /health/
/api/auth/        -> auth-service:8000/api/auth/
/api/events/      -> event-service:8000/api/events/
/admin/           -> control-web:8000/admin/
/reports/         -> control-web:8000/reports/
/dashboard/       -> control-web:8000/dashboard/
/static/          -> static_data
```

Наружу открыть только:

```text
80:80
```

Порт 443 подготовить в документации, но HTTPS можно включить позже.

## Dockerfile для FastAPI

Оба FastAPI Dockerfile должны:

```text
использовать python:3.12-slim;
устанавливать системные зависимости только необходимые;
копировать common;
устанавливать common как пакет;
копировать requirements сервиса;
устанавливать зависимости;
копировать код сервиса;
запускать uvicorn;
```

Добавить `.dockerignore`.

## Dockerfile для Django

Django Dockerfile должен:

```text
использовать python:3.12-slim;
копировать common;
устанавливать common;
устанавливать requirements control-web;
копировать код Django;
запускать gunicorn;
```

`collectstatic` можно выполнять отдельной командой через Makefile/deploy script.

## Безопасность

Требования:

```text
не использовать privileged containers;
не хранить secrets в compose-файлах;
не коммитить .env;
не публиковать PostgreSQL наружу;
использовать restart: unless-stopped;
использовать отдельную Docker-сеть;
не использовать bind-mount кода в production.
```

## Makefile

Обновить команды:

```makefile
build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

migrate:
	docker compose exec control-web python manage.py migrate

collectstatic:
	docker compose exec control-web python manage.py collectstatic --noinput

createsuperuser:
	docker compose exec control-web python manage.py createsuperuser
```

## Документация

Создать `docs/docker.md`:

- что такое каждый контейнер;
- какие volume используются;
- почему PostgreSQL не опубликован наружу;
- как запустить проект;
- как остановить проект;
- как пересобрать проект;
- как смотреть логи;
- как выполнить миграции;
- как проверить health endpoint'ы через Nginx.

## Критерии приемки

- `docker compose up -d --build` поднимает всю систему.
- Снаружи открыт только Nginx на порту 80.
- PostgreSQL доступен только внутри Docker-сети.
- Nginx корректно проксирует `/api/auth/`, `/api/events/`, `/admin/`, `/reports/`, `/dashboard/`.
- Static files Django отдаются через Nginx.
- После перезапуска контейнеров данные PostgreSQL сохраняются.
