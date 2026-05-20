#include "ApiClient.h"

#include <cstring>
#include <HTTPClient.h>

#include "Screen/Page/Main/Wait.h"
#include "Service/Log.h"
#include "config.h"

ApiClient::ApiClient(String baseUrl) : baseUrl_(baseUrl.length() ? baseUrl : Config::API_BASE_URL) {}

// Заменить адрес сервера во время работы, если это потребуется настройкам.
void ApiClient::setBaseUrl(const String& baseUrl) {
    baseUrl_ = baseUrl;
}

// Вернуть базовый адрес без изменения состояния клиента.
const String& ApiClient::baseUrl() const {
    return baseUrl_;
}

// Вернуть последнюю ошибку транспортного уровня.
ApiClient::Error ApiClient::lastError() const {
    return lastError_;
}

// Вернуть HTTP-статус последнего ответа.
int ApiClient::lastStatus() const {
    return lastStatus_;
}

// Выполнить JSON POST и заполнить response разобранным JSON.
bool ApiClient::postJson(const char* path, JsonDocument& request, JsonDocument& response, const char* waitTitle) {
    lastError_ = Error::None;
    lastStatus_ = 0;
    response.clear();

    // Пустой path нельзя склеивать с baseUrl, иначе уйдем в некорректный URL.
    if (path == nullptr || path[0] == '\0') {
        lastError_ = Error::InvalidPath;
        return false;
    }

    String body;
    serializeJson(request, body);

    // Heartbeat идет в фоне, поэтому экран ожидания для него не показываем.
    const bool showWait = waitTitle != nullptr && strcmp(path, "/api/device/heartbeat") != 0;
    Screen::WaitGuard wait(showWait ? waitTitle : nullptr);

    HTTPClient http;
    const String url = baseUrl_ + path;
    Log::info("HTTP POST %s", url.c_str());
    // begin() может провалиться еще до сетевого запроса, например при плохом URL.
    if (!http.begin(url)) {
        Log::error("HTTP begin failed: %s", url.c_str());
        lastError_ = Error::BeginFailed;
        return false;
    }

    http.setConnectTimeout(Config::HTTP_REQUEST_TIMEOUT_MS);
    http.setTimeout(Config::HTTP_REQUEST_TIMEOUT_MS);
    http.addHeader("Content-Type", "application/json");
    const int status = http.POST(body);
    lastStatus_ = status;
    const String httpError = status <= 0 ? http.errorToString(status) : String();
    const String payload = http.getString();
    http.end();

    // Неположительный статус в HTTPClient означает транспортную ошибку, а не HTTP-код сервера.
    if (status <= 0) {
        Log::error("HTTP POST failed: %d %s", status, httpError.c_str());
        lastError_ = status == HTTPC_ERROR_READ_TIMEOUT ? Error::Timeout : Error::RequestFailed;
        return false;
    }

    // Даже при HTTP 200 сервер может вернуть не JSON, это отдельная ошибка протокола.
    DeserializationError error = deserializeJson(response, payload);
    if (error) {
        Log::error("JSON response parse failed: %s", error.c_str());
        lastError_ = Error::JsonParse;
        return false;
    }

    return status >= 200 && status < 300;
}
