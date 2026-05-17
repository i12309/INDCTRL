# Docker

INDCTRL запускается через Docker Compose на одном Linux-сервере. Снаружи публикуется
только Nginx на порту `80`; прикладные сервисы и PostgreSQL доступны только во
внутренней Docker-сети `indctrl`.

## Контейнеры

- `postgres` - PostgreSQL 17, хранит рабочие данные проекта.
- `auth-service` - FastAPI-сервис авторизации ESP32.
- `event-service` - FastAPI-сервис приема событий деталей.
- `control-web` - Django admin, dashboard, отчеты и миграции БД.
- `nginx` - единая HTTP-точка входа.

## Volumes

- `postgres_data` - постоянное хранилище `/var/lib/postgresql/data`; данные
  сохраняются после перезапуска контейнеров.
- `static_data` - собранные Django static files; Nginx отдает их по `/static/`.

## Почему PostgreSQL не опубликован наружу

PostgreSQL не имеет секции `ports`, поэтому порт `5432` не открыт на хосте. Это
уменьшает поверхность атаки: к БД обращаются только контейнеры внутри сети
`indctrl`.

## Первый запуск

```bash
cp .env.example .env
docker compose build
docker compose up -d
docker compose exec control-web python manage.py migrate
docker compose exec control-web python manage.py collectstatic --noinput
docker compose exec control-web python manage.py createsuperuser
```

Эквивалентно через `make`:

```bash
make build
make up
make migrate
make collectstatic
make createsuperuser
```

## Production-запуск

```bash
docker compose -f compose.production.yml build
docker compose -f compose.production.yml up -d
docker compose -f compose.production.yml exec control-web python manage.py migrate
docker compose -f compose.production.yml exec control-web python manage.py collectstatic --noinput
```

Скрипт `deploy/scripts/deploy.sh` выполняет сборку, запуск, миграции и collectstatic
в этом порядке. Миграции не встроены в бесконечный старт контейнера, чтобы ошибка
миграции не превращалась в бесконечный restart-loop.

## Остановка и пересборка

```bash
docker compose down
docker compose build
docker compose up -d
```

`docker compose down` не удаляет named volumes. Чтобы удалить данные PostgreSQL,
нужно явно использовать `docker compose down -v`; для production это опасная
операция.

## Логи

```bash
docker compose logs -f
docker compose logs -f auth-service
docker compose logs -f event-service
docker compose logs -f control-web
docker compose logs -f nginx
```

## Health через Nginx

- `GET /health-auth/` - проверка `auth-service`;
- `GET /health-events/` - проверка `event-service`;
- `GET /health-web/` - проверка `control-web`.

## Маршрутизация Nginx

- `/api/auth/` -> `auth-service:8000/api/auth/`;
- `/api/events/` -> `event-service:8000/api/events/`;
- `/admin/` -> `control-web:8000/admin/`;
- `/reports/` -> `control-web:8000/reports/`;
- `/dashboard/` -> `control-web:8000/dashboard/`;
- `/static/` -> volume `static_data`.

Порт `443` и HTTPS будут добавлены отдельным этапом. Сейчас production-конфигурация
готовит единую HTTP-точку входа на `80:80`.
