#include "DeviceApi.h"

#include <ArduinoJson.h>

#include "Service/Service.h"

// Привести ответ ApiClient к единому результату для экранов.
ApiResult DeviceApi::resultFromResponse(bool httpOk, JsonDocument& response) {
    ApiResult result;
    const ApiClient::Error error = Service::api().lastError();
    result.timedOut = error == ApiClient::Error::Timeout;
    // Транспортные ошибки не содержат JSON error, поэтому переводим их в локальный текст.
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

    // Бизнес-ошибка сервера приходит в поле error и показывается пользователю как есть.
    if (!result.success) {
        const char* error = response["error"] | "Ошибка API";
        result.error = error;
    }
    return result;
}

// Запросить работников, доступных текущему устройству по MAC-адресу.
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
    // Если API вернул ошибку, выходные параметры не трогаем, кроме очищения ниже при успехе.
    if (!result.success) return result;

    machineId = response["machineID"] | 0;
    machineName = String(response["machineName"] | "");
    workers.clear();

    JsonArray rows = response["workers"].as<JsonArray>();
    for (JsonObject row : rows) {
        WorkerData worker;
        worker.userId = row["userID"] | 0;
        worker.fullName = String(row["fullName"] | "");
        // Строки без userID игнорируем, потому что по ним нельзя выполнить login.
        if (worker.userId > 0) workers.push_back(worker);
    }

    return result;
}

// Выполнить login и разобрать sessionID, userID, machineID и workID.
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
    // При ошибке login оставляем ID нулевыми, экран покажет result.error.
    if (!result.success) return result;

    result.sessionId = String(response["sessionID"] | "");
    result.userId = response["userID"] | 0;
    result.machineId = response["machineID"] | 0;
    result.workId = response["workID"] | 0;
    return result;
}

// Завершить текущую смену по sessionID, при наличии PIN передать его серверу.
ApiResult DeviceApi::logout(const String& sessionId, const String& password) {
    JsonDocument request;
    JsonDocument response;
    request["sessionID"] = sessionId;
    // password опционален для обратной совместимости API, но экран закрытия смены его передает.
    if (password.length() > 0) {
        request["password"] = password;
    }
    return resultFromResponse(
        Service::api().postJson("/api/device/logout", request, response, "Завершение смены"),
        response
    );
}

// Отправить фоновый heartbeat активной смены.
ApiResult DeviceApi::heartbeat(const String& sessionId) {
    JsonDocument request;
    JsonDocument response;
    request["sessionID"] = sessionId;
    return resultFromResponse(
        Service::api().postJson("/api/device/heartbeat", request, response, "Проверка связи"),
        response
    );
}

// Загрузить список деталей активной смены.
ApiResult DeviceApi::loadDetails(const String& sessionId, std::vector<DetailData>& details) {
    JsonDocument request;
    JsonDocument response;
    request["sessionID"] = sessionId;

    ApiResult result = resultFromResponse(
        Service::api().postJson("/api/device/details", request, response, "Загрузка деталей"),
        response
    );
    // При ошибке оставляем предыдущий список, чтобы экран мог решить, что показывать.
    if (!result.success) return result;

    details.clear();
    JsonArray rows = response["details"].as<JsonArray>();
    for (JsonObject row : rows) {
        DetailData detail;
        detail.number = row["number"] | 0;
        detail.state = String(row["state"] | "");
        detail.time = String(row["time"] | "");
        // Детали без номера не отображаются, потому что строка таблицы теряет смысл.
        if (detail.number > 0) details.push_back(detail);
    }

    return result;
}
