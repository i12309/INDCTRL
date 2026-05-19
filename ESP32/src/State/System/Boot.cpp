#include "Boot.h"

#include <Arduino.h>

#include "Screen/Page/Main/Info.h"
#include "Screen/Page/Main/Load.h"
#include "Service/Log.h"
#include "Service/WiFiConfig.h"
#include "State/System/Idle.h"
#include "config.h"

Boot::Boot() : State(Type::Boot) {}

void Boot::onEnter() {
    startedAtMs_ = millis();
    Screen::Load::instance().setText("INDCTRL loading...");
    Screen::Load::instance().show();
}

State* Boot::tick() {
    if (millis() - startedAtMs_ < Config::BOOT_SCREEN_MS) return this;

    if (!wifiChecked_) {
        wifiChecked_ = true;

        for (uint8_t attempt = 1; attempt <= Config::WIFI_CONNECT_ATTEMPTS; ++attempt) {
            Log::info("WiFi connect attempt %u/%u", attempt, Config::WIFI_CONNECT_ATTEMPTS);
            if (WiFiConfig::instance().connect(
                    Config::WIFI_SSID,
                    Config::WIFI_PASSWORD,
                    Config::WIFI_CONNECT_TIMEOUT_MS
                )) {
                return new Idle();
            }
        }

        Screen::Info::showRestart("WiFi недоступен", "Проверьте сеть и нажмите OK");
        wifiFailed_ = true;
        return this;
    }

    if (wifiFailed_) return this;
    return new Idle();
}
