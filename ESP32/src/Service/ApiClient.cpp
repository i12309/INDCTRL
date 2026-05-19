#include "ApiClient.h"

#include <HTTPClient.h>

#include "Screen/Page/Main/Wait.h"
#include "Service/Log.h"
#include "config.h"

ApiClient::ApiClient(String baseUrl) : baseUrl_(baseUrl.length() ? baseUrl : Config::API_BASE_URL) {}

void ApiClient::setBaseUrl(const String& baseUrl) {
    baseUrl_ = baseUrl;
}

const String& ApiClient::baseUrl() const {
    return baseUrl_;
}

ApiClient::Error ApiClient::lastError() const {
    return lastError_;
}

int ApiClient::lastStatus() const {
    return lastStatus_;
}

bool ApiClient::postJson(const char* path, JsonDocument& request, JsonDocument& response, const char* waitTitle) {
    lastError_ = Error::None;
    lastStatus_ = 0;
    response.clear();

    if (path == nullptr || path[0] == '\0') {
        lastError_ = Error::InvalidPath;
        return false;
    }

    String body;
    serializeJson(request, body);

    Screen::WaitGuard wait(waitTitle);

    HTTPClient http;
    const String url = baseUrl_ + path;
    Log::info("HTTP POST %s", url.c_str());
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

    if (status <= 0) {
        Log::error("HTTP POST failed: %d %s", status, httpError.c_str());
        lastError_ = status == HTTPC_ERROR_READ_TIMEOUT ? Error::Timeout : Error::RequestFailed;
        return false;
    }

    DeserializationError error = deserializeJson(response, payload);
    if (error) {
        Log::error("JSON response parse failed: %s", error.c_str());
        lastError_ = Error::JsonParse;
        return false;
    }

    return status >= 200 && status < 300;
}
