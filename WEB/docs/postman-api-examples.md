# Postman-примеры для ESP32 API

Базовый адрес для локального запуска через `docker compose`:

```text
http://localhost
```

Во всех `POST` запросах поставь header:

```text
Content-Type: application/json
```

Удобные переменные Postman:

```text
baseUrl=http://localhost
macAddress=AA:BB:CC:DD:EE:FF
userID=1
pin=1234
sessionID=11111111-1111-1111-1111-111111111111
machineID=1
workID=1
detailTypeID=1
qualityPercent=85
```

Перед тестами в админке должны быть созданы:

- активный станок;
- активное устройство с `mac_address`, например `AA:BB:CC:DD:EE:FF`;
- активный пользователь с правом `accounts.use_esp32_api`;
- активная строка графика для этого пользователя и станка;
- активный тип детали.

API возвращает HTTP 200 и для бизнес-ошибок. Признак ошибки в JSON: `"success": false`.

## 1. Health

```http
GET {{baseUrl}}/health/
```

Ожидаемый ответ:

```json
{
  "status": "ok",
  "service": "indctrl"
}
```

## 2. Список доступных работников

```http
POST {{baseUrl}}/api/device/workers
```

Body:

```json
{
  "macAddress": "{{macAddress}}"
}
```

Ожидаемый успешный ответ:

```json
{
  "success": true,
  "machineID": 1,
  "machineName": "Станок 1",
  "workers": [
    {
      "userID": 1,
      "fullName": "Иванов Иван"
    }
  ]
}
```

Если устройство существует, но сейчас нет работников по графику:

```json
{
  "success": true,
  "machineID": 1,
  "machineName": "Станок 1",
  "workers": []
}
```

Ошибка: нет `macAddress`.

```json
{}
```

Ожидаемый ответ:

```json
{
  "success": false,
  "error": "Поле macAddress обязательно"
}
```

Ошибка: неизвестный MAC.

```json
{
  "macAddress": "00:00:00:00:00:00"
}
```

Ожидаемый ответ:

```json
{
  "success": false,
  "error": "Устройство с таким MAC-адресом не найдено"
}
```

## 3. Login

```http
POST {{baseUrl}}/login/pin
```

Body:

```json
{
  "pin": "{{pin}}",
  "macAddress": "{{macAddress}}"
}
```

Ожидаемый успешный ответ:

```json
{
  "success": true,
  "sessionID": "11111111-1111-1111-1111-111111111111",
  "userID": 1,
  "machineID": 1,
  "workID": 1
}
```

Сохрани `sessionID`, `machineID`, `workID` в переменные Postman. Для автоматического сохранения добавь в Tests:

```javascript
const data = pm.response.json();
if (data.success) {
  pm.environment.set("sessionID", data.sessionID);
  pm.environment.set("userID", data.userID);
  pm.environment.set("machineID", data.machineID);
  pm.environment.set("workID", data.workID);
}
```

Повторный login тем же работником на том же станке в том же интервале графика должен вернуть новый `sessionID`, но тот же `workID`.

Ошибка: неверный PIN.

```json
{
  "pin": "0000",
  "macAddress": "{{macAddress}}"
}
```

Ожидаемый ответ:

```json
{
  "success": false,
  "error": "Неверный PIN"
}
```

Ошибка: нет допуска или активного графика на текущие дату/время.

```json
{
  "pin": "{{pin}}",
  "macAddress": "{{macAddress}}"
}
```

Ожидаемый ответ:

```json
{
  "success": false,
  "error": "Нет разрешения или активного расписания на этот станок"
}
```

Ошибка: пользователь не найден, неактивен или без права `use_esp32_api`.

```json
{
  "pin": "{{pin}}",
  "macAddress": "{{macAddress}}"
}
```

Ожидаемый ответ:

```json
{
  "success": false,
  "error": "Пользователь не найден или не является работником"
}
```

Ошибка: активная смена на станке принадлежит другому работнику.

Сценарий:

1. Выполни успешный login пользователем A.
2. Не делай logout.
3. Выполни login пользователем B на тот же `macAddress`.

Ожидаемый ответ:

```json
{
  "success": false,
  "error": "Станок уже занят активной сменой другого работника"
}
```

Ошибка: `userID` не число.

```json
{
  "pin": "abc",
  "macAddress": "{{macAddress}}"
}
```

Ожидаемый ответ:

```json
{
  "success": false,
  "error": "Поле userID должно быть числом"
}
```

## 4. Heartbeat

```http
POST {{baseUrl}}/api/device/heartbeat
```

Body:

```json
{
  "sessionID": "{{sessionID}}"
}
```

Ожидаемый успешный ответ:

```json
{
  "success": true,
  "status": "alive"
}
```

Ошибка: не UUID.

```json
{
  "sessionID": "not-a-uuid"
}
```

Ожидаемый ответ:

```json
{
  "success": false,
  "error": "Поле sessionID должно быть UUID"
}
```

Ошибка: сессия не найдена, истекла, отключена или смена уже не активна.

```json
{
  "sessionID": "11111111-1111-1111-1111-111111111111"
}
```

Ожидаемый ответ:

```json
{
  "success": false,
  "error": "Активная сессия не найдена"
}
```

## 5. Событие детали

```http
POST {{baseUrl}}/api/device/detail
```

Минимальный Body:

```json
{
  "sessionID": "{{sessionID}}",
  "time": "2026-05-18 14:30:00",
  "detail": {
    "number": 1,
    "type": {{detailTypeID}},
    "quality": {{qualityPercent}}
  }
}
```

Ожидаемый ответ для новой детали:

```json
{
  "success": true,
  "status": "saved"
}
```

Повтори тот же запрос с тем же `detail.number`. Ожидаемый ответ для дубля:

```json
{
  "success": true,
  "status": "duplicate"
}
```

Полный Body с дополнительной сверкой IDs:

```json
{
  "sessionID": "{{sessionID}}",
  "userID": {{userID}},
  "machineID": {{machineID}},
  "workID": {{workID}},
  "time": "2026-05-18 14:30:00",
  "detail": {
    "number": 2,
    "type": {{detailTypeID}},
    "quality": {{qualityPercent}}
  }
}
```

Ошибка: `machineID` не совпадает с активной сессией.

```json
{
  "sessionID": "{{sessionID}}",
  "machineID": 999999,
  "time": "2026-05-18 14:30:00",
  "detail": {
    "number": 3,
    "type": {{detailTypeID}},
    "quality": {{qualityPercent}}
  }
}
```

Ожидаемый ответ:

```json
{
  "success": false,
  "error": "machineID не совпадает с активной сессией"
}
```

Ошибка: неверный формат времени.

```json
{
  "sessionID": "{{sessionID}}",
  "time": "18.05.2026 14:30",
  "detail": {
    "number": 4,
    "type": {{detailTypeID}},
    "quality": {{qualityPercent}}
  }
}
```

Ожидаемый ответ:

```json
{
  "success": false,
  "error": "Время события должно быть в формате YYYY-mm-dd HH:mm:ss"
}
```

Ошибка: `detail` не объект.

```json
{
  "sessionID": "{{sessionID}}",
  "time": "2026-05-18 14:30:00",
  "detail": 123
}
```

Ожидаемый ответ:

```json
{
  "success": false,
  "error": "Поле detail должно быть объектом"
}
```

Ошибка: номер детали не положительное число.

```json
{
  "sessionID": "{{sessionID}}",
  "time": "2026-05-18 14:30:00",
  "detail": {
    "number": 0,
    "type": {{detailTypeID}},
    "quality": {{qualityPercent}}
  }
}
```

Ожидаемый ответ:

```json
{
  "success": false,
  "error": "Поле detail.number должно быть больше нуля"
}
```

Ошибка: тип детали не найден или отключен.

```json
{
  "sessionID": "{{sessionID}}",
  "time": "2026-05-18 14:30:00",
  "detail": {
    "number": 5,
    "type": 999999,
    "quality": {{qualityPercent}}
  }
}
```

Ожидаемый ответ:

```json
{
  "success": false,
  "error": "Тип детали не найден или отключен"
}
```

Ошибка: качество детали вне диапазона.

```json
{
  "sessionID": "{{sessionID}}",
  "time": "2026-05-18 14:30:00",
  "detail": {
    "number": 6,
    "type": {{detailTypeID}},
    "quality": 999999
  }
}
```

Ожидаемый ответ:

```json
{
  "success": false,
  "error": "Поле detail.quality должно быть от 0 до 100"
}
```

Ошибки `/api/device/detail` дополнительно сохраняются в `InvalidEvent`.

## 6. Logout

```http
POST {{baseUrl}}/api/device/logout
```

Body:

```json
{
  "sessionID": "{{sessionID}}",
  "pin": "{{pin}}"
}
```

`pin` обязательно. Сервер проверит PIN пользователя текущей активной сессии.

Ожидаемый успешный ответ:

```json
{
  "success": true,
  "status": "finished"
}
```

После logout старый `sessionID` уже нельзя использовать для heartbeat или detail.

Повторный logout тем же `sessionID`:

```json
{
  "sessionID": "{{sessionID}}"
}
```

Ожидаемый ответ:

```json
{
  "success": false,
  "error": "Активная сессия не найдена"
}
```

## 7. Общие ошибки JSON

Некорректный JSON, например:

```json
{
  "macAddress": "{{macAddress}}",
}
```

Ожидаемый ответ:

```json
{
  "success": false,
  "error": "Некорректный JSON"
}
```

JSON верхнего уровня не объект, например массив:

```json
[
  {
    "macAddress": "{{macAddress}}"
  }
]
```

Ожидаемый ответ:

```json
{
  "success": false,
  "error": "JSON должен быть объектом"
}
```

## 8. Рекомендуемый порядок ручного теста

1. `GET /health/`
2. `POST /api/device/workers`
3. `POST /login/pin`
4. Сохранить `sessionID`, `machineID`, `workID`
5. `POST /api/device/heartbeat`
6. `POST /api/device/detail` с `number=1`
7. Повторить `POST /api/device/detail` с `number=1`, проверить `duplicate`
8. `POST /api/device/detail` с `number=2`
9. `POST /api/device/logout`
10. Повторить `heartbeat` со старым `sessionID`, проверить ошибку
