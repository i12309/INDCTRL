#include "WiFiConfig.h"

#include "Screen/Page/Main/Wait.h"
#include "Service/Log.h"

// Вернуть singleton Wi-Fi сервиса.
WiFiConfig& WiFiConfig::instance() {
    static WiFiConfig wifi;
    return wifi;
}

// Включить режим станции, чтобы ESP32 подключался к внешней точке доступа.
void WiFiConfig::init() {
    WiFi.mode(WIFI_STA);
}

// Подключиться к Wi-Fi и дождаться результата в пределах timeoutMs.
bool WiFiConfig::connect(const char* ssid, const char* password, uint32_t timeoutMs) {
    // Без SSID подключение невозможно, сразу возвращаем ошибку.
    if (ssid == nullptr || ssid[0] == '\0') return false;

    Screen::WaitGuard wait("Подключение Wi-Fi");

    WiFi.begin(ssid, password == nullptr ? "" : password);
    const uint32_t start = millis();
    // Ждем подключения короткими задержками, чтобы не перегружать CPU.
    while (WiFi.status() != WL_CONNECTED && millis() - start < timeoutMs) {
        delay(250);
    }

    const bool ok = WiFi.status() == WL_CONNECTED;
    Log::info(ok ? "WiFi connected: %s" : "WiFi connection failed: %s", ssid);
    return ok;
}

// Отключиться от Wi-Fi.
void WiFiConfig::disconnect() {
    WiFi.disconnect();
}

// Проверить статус подключения.
bool WiFiConfig::isConnected() const {
    return WiFi.status() == WL_CONNECTED;
}

// Вернуть SSID только при активном подключении.
String WiFiConfig::ssid() const {
    return isConnected() ? WiFi.SSID() : "";
}

// Вернуть IP только при активном подключении.
String WiFiConfig::ip() const {
    return isConnected() ? WiFi.localIP().toString() : "";
}

// Перевести RSSI в грубый процент для UI/диагностики.
int WiFiConfig::rssiPercent() const {
    if (!isConnected()) return 0;
    return constrain(100 + WiFi.RSSI(), 0, 100);
}
