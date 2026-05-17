# event-service

FastAPI-сервис приема событий о произведенных деталях от ESP32. Сервис проверяет
активную сессию работника, сохраняет деталь в PostgreSQL и идемпотентно обрабатывает
дубли.

## Почему sessionID главный

ESP32 не является доверенным источником `userID`, `machineID` и `workID`.
`event-service` берет эти значения из `AuthSession`, созданной `auth-service`.
Если устройство дополнительно пришлет ID и они не совпадут с сессией, событие будет
отклонено и сохранено в `InvalidEvent`.

## Формат события

```json
{
  "sessionID": "11111111-1111-1111-1111-111111111111",
  "time": "2026-05-16 20:30:00",
  "detail": {
    "number": 1,
    "type": 2,
    "state": 1
  }
}
```

## Endpoint'ы

- `GET /health` - состояние сервиса внутри Docker-сети.
- `GET /health-events/` - состояние сервиса через Nginx.
- `POST /api/events/detail` - прием события детали.

Ответ новой детали:

```json
{"success": true, "status": "saved"}
```

Ответ дубля:

```json
{"success": true, "status": "duplicate"}
```

Ошибка:

```json
{"success": false, "error": "описание ошибки"}
```

## InvalidEvent

В `InvalidEvent` сохраняются:

- битый JSON;
- неверная структура события;
- неизвестный или неактивный `sessionID`;
- истекшая сессия;
- неизвестный тип или состояние детали;
- несовпадение `userID`, `machineID`, `workID` с активной сессией.

Корректно сохраненная деталь не дублирует сырой JSON в БД.

## Защита от дублей

Деталь уникальна по `(user_id, machine_id, work_id, detail_number)`. SQL использует
`ON CONFLICT DO NOTHING`: при повторе запись не создается, а ESP32 получает
`{"success": true, "status": "duplicate"}` и прекращает повторную отправку.

## Переменные окружения

Сервис читает общие переменные из `.env`: `APP_ENV`, `APP_TIMEZONE`,
`POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`,
`POSTGRES_PORT`.

## Запуск в Docker

```bash
docker compose up -d --build event-service
```

Наружу сервис напрямую не публикуется. Доступ идет через Nginx:
`http://localhost/api/events/...`.

## Диагностика и логи

```bash
docker compose logs -f event-service
docker compose exec event-service python --version
```
