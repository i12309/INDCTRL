#pragma once

#include <Arduino.h>
#include <ArduinoJson.h>

class ApiClient {
public:
    enum class Error {
        None,
        InvalidPath,
        BeginFailed,
        RequestFailed,
        Timeout,
        JsonParse
    };

    explicit ApiClient(String baseUrl = "");

    void setBaseUrl(const String& baseUrl);
    const String& baseUrl() const;
    Error lastError() const;
    int lastStatus() const;

    bool postJson(const char* path, JsonDocument& request, JsonDocument& response, const char* waitTitle = nullptr);

private:
    String baseUrl_;
    Error lastError_ = Error::None;
    int lastStatus_ = 0;
};
