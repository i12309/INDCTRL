#pragma once

#include <Arduino.h>
#include <WiFi.h>

class WiFiConfig {
public:
    static WiFiConfig& instance();

    void init();
    bool connect(const char* ssid, const char* password, uint32_t timeoutMs = 10000);
    void disconnect();
    bool isConnected() const;
    String ssid() const;
    String ip() const;
    int rssiPercent() const;

private:
    WiFiConfig() = default;
};
