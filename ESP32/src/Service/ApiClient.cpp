#include "ApiClient.h"

#include <HTTPClient.h>

#include "Service/Log.h"
#include "config.h"

ApiClient::ApiClient(String baseUrl) : baseUrl_(baseUrl.length() ? baseUrl : Config::API_BASE_URL) {}

void ApiClient::setBaseUrl(const String& baseUrl) {
    baseUrl_ = baseUrl;
}

const String& ApiClient::baseUrl() const {
    return baseUrl_;
}

bool ApiClient::postJson(const char* path, JsonDocument& request, JsonDocument& response) {
    if (path == nullptr || path[0] == '\0') return false;

    String body;
    serializeJson(request, body);

    HTTPClient http;
    const String url = baseUrl_ + path;
    if (!http.begin(url)) {
        Log::error("HTTP begin failed: %s", url.c_str());
        return false;
    }

    http.addHeader("Content-Type", "application/json");
    const int status = http.POST(body);
    const String payload = http.getString();
    http.end();

    if (status <= 0) {
        Log::error("HTTP POST failed: %d", status);
        return false;
    }

    DeserializationError error = deserializeJson(response, payload);
    if (error) {
        Log::error("JSON response parse failed: %s", error.c_str());
        return false;
    }

    return status >= 200 && status < 300;
}
