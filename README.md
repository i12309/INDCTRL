# INDCTRL

INDCTRL - система контроля работы станков на одном Linux-сервере. Проект состоит из
нескольких контейнеров, которые запускаются через Docker Compose и используют одну
PostgreSQL-БД.

## Сервисы

- `auth-service` - FastAPI-сервис авторизации работников на ESP32-терминалах,
  создания смен, heartbeat и logout.
- `event-service` - FastAPI-сервис приема событий о произведенных деталях от ESP32.
- `control-web` - Django-сервис с административной панелью, dashboard, отчетами и
  миграциями БД.
- `postgres` - общая PostgreSQL-БД.
- `nginx` - единая HTTP-точка входа.

## Почему PostgreSQL

Проект сразу рассчитан на рабочую эксплуатацию, общую БД для нескольких сервисов и
миграции через Django. SQLite для такой схемы не подходит: он ограничивает
конкурентную запись, сложнее обслуживается в контейнерах и не отражает production-
окружение.

## Почему Docker Compose

Все компоненты должны запускаться на одном Linux-сервере предприятия. Docker Compose
дает повторяемый запуск, изолированные контейнеры, общий internal network,
healthcheck PostgreSQL и независимые образы сервисов без установки Python-зависимостей
на хост.

## Почему admin и отчеты в control-web

Django уже содержит admin, ORM, формы, шаблоны и систему пользователей. Поэтому
админка, dashboard и отчеты находятся в одном сервисе `control-web`, используют один
набор моделей и один источник миграций. FastAPI-сервисы читают и пишут в ту же БД
напрямую, но не запускают миграции.

## Первый запуск

```bash
cp .env.example .env
docker compose up -d --build
docker compose ps
```

После старта:

- `http://localhost/health-web/` - health Django `control-web` через Nginx;
- `http://localhost/health-auth/` - health `auth-service` через Nginx;
- `http://localhost/health-events/` - health `event-service` через Nginx.

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

Если `make` недоступен, используйте команды Docker Compose напрямую, например
`docker compose up -d --build`.

## Документация

Основные документы находятся в `docs/`:

- `docs/architecture.md` - архитектура;
- `docs/database.md` - БД и миграции;
- `docs/docker.md` - контейнеры;
- `docs/env.md` - переменные окружения;
- `docs/esp32-api.md` - последовательность работы ESP32 и примеры JSON;
- `docs/final-checklist.md` - финальный чеклист приемки;
- `docs/services/` - документы сервисов;
- `docs/linux/runbook.md` - общий runbook эксплуатации на Linux;
- `docs/linux/` - дополнительные инструкции Linux;
- `docs/backup/` - резервное копирование PostgreSQL.

## Логи

```bash
docker compose logs -f
docker compose logs -f auth-service
docker compose logs -f event-service
docker compose logs -f control-web
docker compose logs -f nginx
```

## Миграции

Django является источником структуры БД:

```bash
make migrate
```

Миграции создают доменные таблицы INDCTRL и начальные справочники ролей и состояний
деталей. Все изменения схемы БД должны проходить через `control-web`.

## Администратор Django

```bash
make createsuperuser
```

Админка доступна по адресу `http://localhost/admin/`.
