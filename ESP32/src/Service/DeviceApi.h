#pragma once

#include <Arduino.h>
#include <ArduinoJson.h>
#include <vector>

#include "Data.h"

// Унифицированный результат API-вызова без полезной нагрузки.
struct ApiResult {
    // true, если сервер вернул success=true.
    bool success = false;
    // true, если ошибка вызвана таймаутом и экран не нужно сбрасывать.
    bool timedOut = false;
    // Текст ошибки для показа пользователю.
    String error;
};

// Результат успешного или неуспешного login.
struct LoginResult {
    // true, если login прошел успешно.
    bool success = false;
    // true, если сервер не ответил за таймаут.
    bool timedOut = false;
    // Текст ошибки входа.
    String error;
    // Новый sessionID активной смены.
    String sessionId;
    // Пользователь, подтвержденный сервером.
    int userId = 0;
    // Станок, подтвержденный сервером.
    int machineId = 0;
    // ID рабочей смены, созданной или продолженной сервером.
    int workId = 0;
};

// Типизированная обертка над бизнес-endpoint'ами устройства.
class DeviceApi {
public:
    // Загрузить список работников, доступных этому MAC-адресу.
    static ApiResult loadWorkers(const String& macAddress, int& machineId, String& machineName, std::vector<WorkerData>& workers);
    // Выполнить вход работника и получить sessionID активной смены.
    static LoginResult login(int userId, const String& password, const String& macAddress);
    // Завершить смену по текущему sessionID; password передается для подтверждения, если введен.
    static ApiResult logout(const String& sessionId, const String& password = String());
    // Продлить активность текущей смены на сервере.
    static ApiResult heartbeat(const String& sessionId);
    // Загрузить детали текущей смены для экрана Details.
    static ApiResult loadDetails(const String& sessionId, std::vector<DetailData>& details);

private:
    // Преобразовать HTTP/JSON-ответ в общий ApiResult и сохранить текст ошибки.
    static ApiResult resultFromResponse(bool httpOk, JsonDocument& response);
};
