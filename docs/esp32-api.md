# API для ESP32-разработчика

ESP32 работает с Django API через Nginx. Базовый адрес в примерах:
`http://localhost`.

## Последовательность работы

1. ESP32 отправляет `macAddress` и получает список работников.
2. Работник выбирает ФИО и вводит пароль.
3. ESP32 отправляет login.
4. ESP32 получает `sessionID`, `userID`, `machineID`, `workID`.
5. ESP32 отправляет события деталей с `sessionID`.
6. ESP32 периодически отправляет heartbeat.
7. При завершении работы ESP32 отправляет logout.

## POST /api/device/workers

Запрос:

```json
{
  "macAddress": "AA:BB:CC:DD:EE:FF"
}
```

Ответ:

```json
{
  "success": true,
  "machineID": 1,
  "machineName": "Токарный станок 1",
  "workers": [
    {"userID": 10, "fullName": "Иванов Иван Иванович"}
  ]
}
```

## POST /api/device/login

Запрос:

```json
{
  "userID": 10,
  "password": "1234",
  "macAddress": "AA:BB:CC:DD:EE:FF"
}
```

Ответ:

```json
{
  "success": true,
  "sessionID": "11111111-1111-1111-1111-111111111111",
  "userID": 10,
  "machineID": 1,
  "workID": 100
}
```

## POST /api/device/detail

Рекомендуемый запрос:

```json
{
  "sessionID": "11111111-1111-1111-1111-111111111111",
  "time": "2026-05-18 14:30:00",
  "detail": {
    "number": 1,
    "type": 1,
    "state": 1
  }
}
```

Можно дополнительно передать `userID`, `machineID`, `workID`; Django сверит их с
активной сессией.

Ответ новой детали:

```json
{"success": true, "status": "saved"}
```

Ответ дубля:

```json
{"success": true, "status": "duplicate"}
```

Дубль определяется по `userID`, `machineID`, `workID`, `detail.number`.

## POST /api/device/heartbeat

Запрос:

```json
{
  "sessionID": "11111111-1111-1111-1111-111111111111"
}
```

Ответ:

```json
{"success": true, "status": "alive"}
```

## POST /api/device/logout

Запрос:

```json
{
  "sessionID": "11111111-1111-1111-1111-111111111111"
}
```

Ответ:

```json
{"success": true, "status": "finished"}
```

## Ошибки

Типовой ответ:

```json
{"success": false, "error": "Активная сессия не найдена"}
```

Если ошибка произошла при отправке детали, Django сохраняет исходный body и
причину ошибки в `InvalidEvent`.

## Health

```bash
GET /health-web/
```
