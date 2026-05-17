# auth-service API

`auth-service` - FastAPI-сервис авторизации работников на ESP32. Сервис
определяет станок по `macAddress`, возвращает доступных работников, создает
смену и сессию, принимает heartbeat и завершает смену.

Все ошибки прикладного уровня возвращаются в формате:

```json
{"success": false, "error": "описание ошибки"}
```

## GET /health

Назначение: проверить, что контейнер отвечает.

Пример запроса:

```bash
curl http://localhost/health-auth/
```

Успешный ответ:

```json
{"status": "ok", "service": "auth-service"}
```

Пример ошибки: если контейнер не запущен, Nginx вернет `502 Bad Gateway`.

Что меняется в БД: ничего.

## POST /api/auth/device/workers

Назначение: получить работников, которым сейчас разрешено работать на станке,
к которому привязано ESP32-устройство.

Пример запроса:

```json
{
  "macAddress": "AA:BB:CC:DD:EE:FF"
}
```

Успешный ответ:

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

Пример ошибки:

```json
{"success": false, "error": "Устройство с таким MAC-адресом не найдено"}
```

Что меняется в БД: ничего. Сервис читает `devices`, `machines`, `users`,
`roles`, `user_machine_permissions`, `user_machine_schedules`.

## POST /api/auth/login

Назначение: авторизовать работника на станке, создать рабочую смену `Work` и
сессию `AuthSession`.

Пример запроса:

```json
{
  "userID": 10,
  "password": "1234",
  "macAddress": "AA:BB:CC:DD:EE:FF"
}
```

Успешный ответ:

```json
{
  "success": true,
  "sessionID": "11111111-1111-1111-1111-111111111111",
  "userID": 10,
  "machineID": 1,
  "workID": 100
}
```

Примеры ошибок:

```json
{"success": false, "error": "Неверный пароль"}
```

```json
{"success": false, "error": "Станок уже занят активной сменой"}
```

Что меняется в БД: создаются `works` со статусом `active` и `auth_sessions` с
`is_active=true`. Перед записью проверяются активность устройства и станка,
роль `worker`, пароль, разрешение, расписание и отсутствие активной смены на
станке.

## POST /api/auth/logout

Назначение: завершить активную смену по `sessionID`.

Пример запроса:

```json
{
  "sessionID": "11111111-1111-1111-1111-111111111111"
}
```

Успешный ответ:

```json
{"success": true, "status": "finished"}
```

Пример ошибки:

```json
{"success": false, "error": "Активная сессия не найдена"}
```

Что меняется в БД: `auth_sessions.is_active` становится `false`, связанный
`works.status` становится `finished`, заполняется `works.finished_at`.

## POST /api/auth/heartbeat

Назначение: подтвердить, что ESP32 и работник продолжают активную смену.

Пример запроса:

```json
{
  "sessionID": "11111111-1111-1111-1111-111111111111"
}
```

Успешный ответ:

```json
{"success": true, "status": "alive"}
```

Пример ошибки:

```json
{"success": false, "error": "Активная сессия не найдена"}
```

Что меняется в БД: обновляются `works.last_seen_at` и `works.updated_at`.
Сессия должна быть активной и не истекшей.
