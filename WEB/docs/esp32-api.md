# API для ESP32

ESP32 работает с Django API через Nginx. Базовый адрес в примерах:
`http://localhost`.

## Рабочий поток

1. После загрузки ESP32 переходит в Idle и показывает экран Load.
2. Тап по Load открывает ввод PIN.
3. ESP32 отправляет `POST /login/pin` с `pin` и `macAddress`; старый `POST /api/device/login` оставлен совместимым alias.
4. Если PIN принадлежит администратору, сервер возвращает `isAdmin=true`, а ESP32 открывает список сотрудников.
5. Если PIN принадлежит работнику, сервер создает или продолжает смену и возвращает `sessionID`, `userID`, `machineID`, `workID`.
6. ESP32 отправляет события деталей и heartbeat с текущим `sessionID`.
7. При завершении смены ESP32 отправляет `POST /api/device/logout` с `sessionID` и PIN пользователя активной смены.

PIN хранится в базе как `pin_hash`. Пароль Django нужен только для входа в admin и web-отчеты; пользователь может не иметь пароля и при этом входить на ESP32 по PIN.

Работник появляется в списке и может выполнить login только если пользователь активен, имеет право `accounts.use_esp32_api`, допущен к станку и попадает в активное расписание работы.

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

## POST /login/pin

Основной PIN-login endpoint для ESP32. `POST /api/device/login` работает как совместимый alias.

Запрос:

```json
{
  "pin": "1234",
  "macAddress": "AA:BB:CC:DD:EE:FF"
}
```

Ответ работника:

```json
{
  "success": true,
  "isAdmin": false,
  "sessionID": "11111111-1111-1111-1111-111111111111",
  "userID": 10,
  "fullName": "Иванов Иван Иванович",
  "machineID": 1,
  "workID": 100
}
```

Ответ администратора:

```json
{
  "success": true,
  "isAdmin": true,
  "userID": 1,
  "fullName": "Администратор",
  "machineID": 1,
  "machineName": "Токарный станок 1"
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
    "quality": 85
  }
}
```

Можно дополнительно передать `userID`, `machineID`, `workID`; Django сверит их с активной сессией.

Ответ новой детали:

```json
{"success": true, "status": "saved"}
```

Ответ дубля:

```json
{"success": true, "status": "duplicate"}
```

Дубль определяется по `userID`, `machineID`, `workID`, `detail.number`.

## POST /api/device/details

Запрос:

```json
{
  "sessionID": "11111111-1111-1111-1111-111111111111"
}
```

Ответ:

```json
{
  "success": true,
  "details": [
    {"number": 1, "quality": 85, "state": "85%", "time": "2026-05-18 14:30:00"}
  ]
}
```

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
  "sessionID": "11111111-1111-1111-1111-111111111111",
  "pin": "1234"
}
```

Поле `pin` обязательно. Django сверяет PIN с пользователем активной сессии. ESP32 не должен выполнять повторный login перед logout.

Ответ:

```json
{"success": true, "status": "finished"}
```

## Ошибки

Типовой ответ:

```json
{"success": false, "error": "Активная сессия не найдена"}
```

Если ошибка произошла при отправке детали, Django сохраняет исходный body и причину ошибки в `InvalidEvent`.

## Health

```bash
GET /health-web/
```
