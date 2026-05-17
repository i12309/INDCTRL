# API для ESP32-разработчика

ESP32 общается с сервером только через Nginx по HTTP. В production базовый адрес
замените на адрес сервера, например `http://indctrl.example.local`.

## Последовательность работы

1. ESP32 отправляет `macAddress` и получает список работников.
2. Работник выбирает ФИО и вводит пароль.
3. ESP32 отправляет login.
4. ESP32 получает `sessionID`, `userID`, `machineID`, `workID`.
5. ESP32 отправляет события деталей с `sessionID`.
6. ESP32 периодически отправляет heartbeat.
7. При завершении работы ESP32 отправляет logout.

## 1. Получить список работников

`POST /api/auth/device/workers`

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
    {"userID": 10, "fullName": "Иванов Иван Иванович"},
    {"userID": 11, "fullName": "Петров Петр Петрович"}
  ]
}
```

Если `workers` пустой, на этот момент нет работников с активным разрешением и
расписанием для станка.

## 2. Login работника

`POST /api/auth/login`

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

ESP32 должен сохранить эти значения в оперативном состоянии текущей смены.
Главное значение для дальнейших запросов - `sessionID`.

## 3. Отправка детали

`POST /api/events/detail`

Рекомендуемый минимальный JSON:

```json
{
  "sessionID": "11111111-1111-1111-1111-111111111111",
  "time": "2026-05-17 14:30:00",
  "detail": {
    "number": 1,
    "type": 1,
    "state": 1
  }
}
```

Расширенный JSON для диагностики:

```json
{
  "sessionID": "11111111-1111-1111-1111-111111111111",
  "userID": 10,
  "machineID": 1,
  "workID": 100,
  "time": "2026-05-17 14:30:00",
  "detail": {
    "number": 1,
    "type": 1,
    "state": 1
  }
}
```

Ответ для новой детали:

```json
{"success": true, "status": "saved"}
```

Ответ для повтора:

```json
{"success": true, "status": "duplicate"}
```

Повторная отправка того же `detail.number` в рамках той же смены безопасна:
сервер не создаст дубль.

## 4. Heartbeat

`POST /api/auth/heartbeat`

```json
{
  "sessionID": "11111111-1111-1111-1111-111111111111"
}
```

Ответ:

```json
{"success": true, "status": "alive"}
```

Heartbeat обновляет время последней активности смены. Интервал отправки должен
быть меньше значения `HEARTBEAT_MAX_AGE_SECONDS` на сервере.

## 5. Logout

`POST /api/auth/logout`

```json
{
  "sessionID": "11111111-1111-1111-1111-111111111111"
}
```

Ответ:

```json
{"success": true, "status": "finished"}
```

После logout ESP32 должен удалить локальную текущую сессию и вернуться к выбору
работника.

## Обработка ошибок на ESP32

Типовой ответ ошибки:

```json
{"success": false, "error": "Активная сессия не найдена"}
```

Рекомендации:

- при ошибке login показать текст `error` работнику;
- при ошибке события детали сохранить событие локально и повторить позже, если
  причина похожа на сетевой сбой;
- при `Активная сессия не найдена` запросить новый login;
- при `duplicate` считать событие успешно обработанным и не повторять его.

## Health endpoints

```bash
GET /health-auth/
GET /health-events/
GET /health-web/
```
