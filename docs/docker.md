# Docker

INDCTRL запускается через Docker Compose на одном Linux-сервере. После перехода
на Django-only в рабочей архитектуре осталось три контейнера:

- `indctrl` - web-интерфейс, admin, dashboard, отчеты, API для ESP32 и миграции;
- `postgres` - PostgreSQL 17 с рабочими данными;
- `nginx` - единая HTTP-точка входа на порт `80`.

PostgreSQL и Django не публикуются наружу напрямую. Внешние запросы принимает
только Nginx.

## Volumes

- `postgres_data` - постоянное хранилище `/var/lib/postgresql/data`;
- `static_data` - собранные Django static files для отдачи через `/static/`.

## Первый запуск

```bash
cp .env.example .env
docker compose build
docker compose up -d
docker compose exec indctrl python manage.py migrate
docker compose exec indctrl python manage.py collectstatic --noinput
docker compose exec indctrl python manage.py createsuperuser
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
docker compose -f compose.production.yml exec indctrl python manage.py migrate
docker compose -f compose.production.yml exec indctrl python manage.py collectstatic --noinput
```

Скрипт `deploy/scripts/deploy.sh` выполняет эти шаги автоматически.

## Остановка и пересборка

```bash
docker compose down
docker compose build
docker compose up -d
```

`docker compose down` не удаляет named volumes. Для удаления данных PostgreSQL
нужно явно выполнить `docker compose down -v`; в production это опасная операция.

## Логи

```bash
docker compose logs -f
docker compose logs -f indctrl
docker compose logs -f nginx
docker compose logs -f postgres
```

## Health

- `GET /health-web/` - проверка Django через Nginx;
- `GET /health/` - тот же endpoint внутри Django.

Ожидаемый ответ:

```json
{"status": "ok", "service": "indctrl"}
```

## Маршрутизация Nginx

- `/api/device/workers` -> Django API;
- `/api/device/login` -> Django API;
- `/api/device/heartbeat` -> Django API;
- `/api/device/logout` -> Django API;
- `/api/device/detail` -> Django API;
- `/admin/` -> Django admin;
- `/reports/` -> отчеты;
- `/dashboard/` -> dashboard;
- `/static/` -> volume `static_data`.
