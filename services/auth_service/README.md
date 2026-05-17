# auth-service

FastAPI-сервис авторизации работников на ESP32-терминалах. Сервис определяет станок
по MAC-адресу ESP32, выдает список доступных работников, проверяет пароль, создает
рабочую смену, создает сессию, принимает heartbeat и завершает смену.

## Переменные окружения

Сервис читает общие переменные из `.env`: `APP_ENV`, `APP_TIMEZONE`,
`POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`,
`POSTGRES_PORT`, `SESSION_TTL_MINUTES`, `HEARTBEAT_MAX_AGE_SECONDS`.

## Запуск в Docker

```bash
docker compose up -d --build auth-service
```

Наружу сервис напрямую не публикуется. Доступ идет через Nginx:
`http://localhost/api/auth/...`.

## Endpoint'ы

- `GET /health` - состояние сервиса.
- `POST /api/auth/device/workers` - список работников, доступных на станке сейчас.
- `POST /api/auth/login` - вход работника, создание `Work` и `AuthSession`.
- `POST /api/auth/logout` - завершение смены.
- `POST /api/auth/heartbeat` - обновление активности смены.

## Примеры

Список работников:

```json
{
  "macAddress": "AA:BB:CC:DD:EE:FF"
}
```

Ответ:

```json
{
  "success": true,
  "machineID": 321,
  "machineName": "Станок №1",
  "workers": [
    {"userID": 123, "fullName": "Иванов Иван Иванович"}
  ]
}
```

Login:

```json
{
  "userID": 123,
  "password": "1234",
  "macAddress": "AA:BB:CC:DD:EE:FF"
}
```

Ответ:

```json
{
  "success": true,
  "sessionID": "11111111-1111-1111-1111-111111111111",
  "userID": 123,
  "machineID": 321,
  "workID": 111
}
```

Logout и heartbeat:

```json
{
  "sessionID": "11111111-1111-1111-1111-111111111111"
}
```

Типовой ответ logout:

```json
{"success": true, "status": "finished"}
```

Типовой ответ heartbeat:

```json
{"success": true, "status": "alive"}
```

## Типовые ошибки

- неизвестный MAC: `{"success": false, "error": "Устройство с таким MAC-адресом не найдено"}`;
- неверный пароль: `{"success": false, "error": "Неверный пароль"}`;
- нет разрешения: `{"success": false, "error": "Нет разрешения работать на этом станке"}`;
- нет расписания: `{"success": false, "error": "Для работника нет активного расписания на этот станок"}`;
- станок занят: `{"success": false, "error": "Станок уже занят активной сменой"}`.

## Диагностика и логи

```bash
docker compose logs -f auth-service
docker compose exec auth-service python --version
```
