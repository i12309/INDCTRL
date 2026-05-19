#pragma once

#include <Arduino.h>
#include <ArduinoJson.h>

class ApiClient {
public:
    explicit ApiClient(String baseUrl = "");

    void setBaseUrl(const String& baseUrl);
    const String& baseUrl() const;

    bool postJson(const char* path, JsonDocument& request, JsonDocument& response);

private:
    String baseUrl_;
};
