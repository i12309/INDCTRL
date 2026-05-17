# event-service

FastAPI-сервис приема событий о произведенных деталях от ESP32. В следующих этапах
здесь появятся endpoint'ы записи событий и защита от дублей.

## Переменные окружения

Сервис читает общие переменные из `.env`: `APP_ENV`, `APP_TIMEZONE`,
`POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`,
`POSTGRES_PORT`.

## Запуск в Docker

```bash
docker compose up -d --build event-service
```

## Endpoint'ы

- `GET /health` - состояние сервиса.

Через Nginx локально: `GET /event/health`.

## Диагностика и логи

```bash
docker compose logs -f event-service
docker compose exec event-service python --version
```
