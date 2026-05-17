# auth-service

FastAPI-сервис авторизации работников на ESP32-терминалах. В следующих этапах здесь
будут login/logout, создание смены и heartbeat.

## Переменные окружения

Сервис читает общие переменные из `.env`: `APP_ENV`, `APP_TIMEZONE`,
`POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`,
`POSTGRES_PORT`, `SESSION_TTL_MINUTES`, `HEARTBEAT_MAX_AGE_SECONDS`.

## Запуск в Docker

```bash
docker compose up -d --build auth-service
```

## Endpoint'ы

- `GET /health` - состояние сервиса.

Через Nginx локально: `GET /auth/health`.

## Диагностика и логи

```bash
docker compose logs -f auth-service
docker compose exec auth-service python --version
```
