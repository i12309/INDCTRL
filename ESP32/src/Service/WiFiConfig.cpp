#include "WiFiConfig.h"

#include "Screen/Page/Main/Wait.h"
#include "Service/Log.h"

WiFiConfig& WiFiConfig::instance() {
    static WiFiConfig wifi;
    return wifi;
}

void WiFiConfig::init() {
    WiFi.mode(WIFI_STA);
}

bool WiFiConfig::connect(const char* ssid, const char* password, uint32_t timeoutMs) {
    if (ssid == nullptr || ssid[0] == '\0') return false;

    Screen::WaitGuard wait("Подключение Wi-Fi");

    WiFi.begin(ssid, password == nullptr ? "" : password);
    const uint32_t start = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - start < timeoutMs) {
        delay(250);
    }

    const bool ok = WiFi.status() == WL_CONNECTED;
    Log::info(ok ? "WiFi connected: %s" : "WiFi connection failed: %s", ssid);
    return ok;
}

void WiFiConfig::disconnect() {
    WiFi.disconnect();
}

bool WiFiConfig::isConnected() const {
    return WiFi.status() == WL_CONNECTED;
}

String WiFiConfig::ssid() const {
    return isConnected() ? WiFi.SSID() : "";
}

String WiFiConfig::ip() const {
    return isConnected() ? WiFi.localIP().toString() : "";
}

int WiFiConfig::rssiPercent() const {
    if (!isConnected()) return 0;
    return constrain(100 + WiFi.RSSI(), 0, 100);
}
