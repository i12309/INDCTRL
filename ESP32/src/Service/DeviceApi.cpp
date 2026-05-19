#include "DeviceApi.h"

#include <ArduinoJson.h>

#include "Service/Service.h"

ApiResult DeviceApi::resultFromResponse(bool httpOk, JsonDocument& response) {
    ApiResult result;
    const ApiClient::Error error = Service::api().lastError();
    result.timedOut = error == ApiClient::Error::Timeout;
    if (!httpOk && error != ApiClient::Error::None) {
        switch (error) {
            case ApiClient::Error::Timeout:
                result.error = "Сервер не ответил";
                break;
            case ApiClient::Error::BeginFailed:
            case ApiClient::Error::RequestFailed:
                result.error = "Сервер недоступен";
                break;
            case ApiClient::Error::JsonParse:
                result.error = "Некорректный ответ сервера";
                break;
            case ApiClient::Error::InvalidPath:
                result.error = "Некорректный запрос";
                break;
            case ApiClient::Error::None:
                break;
        }
        return result;
    }

    result.success = httpOk && response["success"].as<bool>();

    if (!result.success) {
        const char* error = response["error"] | "Ошибка API";
        result.error = error;
    }
    return result;
}

ApiResult DeviceApi::loadWorkers(const String& macAddress,
                                 int& machineId,
                                 String& machineName,
                                 std::vector<WorkerData>& workers) {
    JsonDocument request;
    JsonDocument response;
    request["macAddress"] = macAddress;

    ApiResult result = resultFromResponse(
        Service::api().postJson("/api/device/workers", request, response, "Загрузка сотрудников"),
        response
    );
    if (!result.success) return result;

    machineId = response["machineID"] | 0;
    machineName = String(response["machineName"] | "");
    workers.clear();

    JsonArray rows = response["workers"].as<JsonArray>();
    for (JsonObject row : rows) {
        WorkerData worker;
        worker.userId = row["userID"] | 0;
        worker.fullName = String(row["fullName"] | "");
        if (worker.userId > 0) workers.push_back(worker);
    }

    return result;
}

LoginResult DeviceApi::login(int userId, const String& password, const String& macAddress) {
    JsonDocument request;
    JsonDocument response;
    request["userID"] = userId;
    request["password"] = password;
    request["macAddress"] = macAddress;

    ApiResult api = resultFromResponse(
        Service::api().postJson("/api/device/login", request, response, "Вход сотрудника"),
        response
    );
    LoginResult result;
    result.success = api.success;
    result.timedOut = api.timedOut;
    result.error = api.error;
    if (!result.success) return result;

    result.sessionId = String(response["sessionID"] | "");
    result.userId = response["userID"] | 0;
    result.machineId = response["machineID"] | 0;
    result.workId = response["workID"] | 0;
    return result;
}

ApiResult DeviceApi::logout(const String& sessionId) {
    JsonDocument request;
    JsonDocument response;
    request["sessionID"] = sessionId;
    return resultFromResponse(
        Service::api().postJson("/api/device/logout", request, response, "Завершение смены"),
        response
    );
}

ApiResult DeviceApi::heartbeat(const String& sessionId) {
    JsonDocument request;
    JsonDocument response;
    request["sessionID"] = sessionId;
    return resultFromResponse(
        Service::api().postJson("/api/device/heartbeat", request, response, "Проверка связи"),
        response
    );
}

ApiResult DeviceApi::loadDetails(const String& sessionId, std::vector<DetailData>& details) {
    JsonDocument request;
    JsonDocument response;
    request["sessionID"] = sessionId;

    ApiResult result = resultFromResponse(
        Service::api().postJson("/api/device/details", request, response, "Загрузка деталей"),
        response
    );
    if (!result.success) return result;

    details.clear();
    JsonArray rows = response["details"].as<JsonArray>();
    for (JsonObject row : rows) {
        DetailData detail;
        detail.number = row["number"] | 0;
        detail.state = String(row["state"] | "");
        detail.time = String(row["time"] | "");
        if (detail.number > 0) details.push_back(detail);
    }

    return result;
}
