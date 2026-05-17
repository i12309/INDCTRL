# INDCTRL

INDCTRL - Django-only система контроля работы станков на одном Linux-сервере.
Проект использует PostgreSQL, Nginx и Docker Compose.

## Состав

- `indctrl` - web-интерфейс, Django admin, dashboard, отчеты, API для ESP32 и
  миграции БД;
- `postgres` - общая PostgreSQL-БД;
- `nginx` - единая HTTP-точка входа.

Отдельных FastAPI-сервисов в рабочей архитектуре больше нет: API для ESP32
реализован внутри Django.

## API для ESP32

- `POST /api/device/workers`
- `POST /api/device/login`
- `POST /api/device/heartbeat`
- `POST /api/device/logout`
- `POST /api/device/detail`

Подробные JSON-примеры находятся в [docs/esp32-api.md](docs/esp32-api.md).

## Первый запуск

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec indctrl python manage.py migrate
docker compose exec indctrl python manage.py collectstatic --noinput
docker compose exec indctrl python manage.py createsuperuser
docker compose ps
```

После старта:

- `http://localhost/health-web/` - health Django через Nginx;
- `http://localhost/admin/` - Django admin;
- `http://localhost/dashboard/current-workers/` - текущие смены;
- `http://localhost/reports/details/` - отчет по деталям.

## Команды Docker Compose

```bash
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

Если `make` недоступен, используйте команды Docker Compose напрямую.

## Документация

- [docs/architecture.md](docs/architecture.md) - Django-only архитектура;
- [docs/database.md](docs/database.md) - БД и миграции;
- [docs/docker.md](docs/docker.md) - Docker Compose;
- [docs/env.md](docs/env.md) - переменные окружения;
- [docs/esp32-api.md](docs/esp32-api.md) - API для ESP32;
- [docs/web-interface.md](docs/web-interface.md) - web-интерфейс и роли;
- [docs/service.md](docs/service.md) - Django-сервис;
- [docs/linux/runbook.md](docs/linux/runbook.md) - runbook Linux-сервера;
- [docs/backup/](docs/backup) - backup и restore PostgreSQL;
- [docs/final-checklist.md](docs/final-checklist.md) - финальный чеклист.

## Логи

```bash
docker compose logs -f
docker compose logs -f indctrl
docker compose logs -f nginx
docker compose logs -f postgres
```

## Миграции

Django является единственным источником структуры БД:

```bash
make migrate
```

Все изменения схемы БД должны проходить через Django-модели и миграции.
