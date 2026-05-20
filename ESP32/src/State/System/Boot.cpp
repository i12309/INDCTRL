#include "Boot.h"

#include <Arduino.h>

#include "Screen/Page/Main/Info.h"
#include "Screen/Page/Main/Load.h"
#include "Service/Log.h"
#include "Service/WiFiConfig.h"
#include "State/System/Idle.h"
#include "config.h"

Boot::Boot() : State(Type::Boot) {}

// Показать Load и начать отсчет минимального времени заставки.
void Boot::onEnter() {
    startedAtMs_ = millis();
    Screen::Load::instance().setText("INDCTRL loading...");
    Screen::Load::instance().show();
}

// Подключить Wi-Fi, затем ждать касания пользователя перед переходом к списку.
State* Boot::tick() {
    // Wi-Fi уже готов: дальше не дергаем сеть и только ждем касание Load.
    if (readyForUser_) {
        if (Screen::Load::instance().continueRequested()) return new Idle();
        return this;
    }

    // Даем экрану Load стабильно появиться перед тяжелой сетевой операцией.
    if (millis() - startedAtMs_ < Config::BOOT_SCREEN_MS) return this;

    // Подключение к Wi-Fi выполняется один раз, чтобы tick не запускал попытки бесконечно.
    if (!wifiChecked_) {
        wifiChecked_ = true;

        for (uint8_t attempt = 1; attempt <= Config::WIFI_CONNECT_ATTEMPTS; ++attempt) {
            Log::info("WiFi connect attempt %u/%u", attempt, Config::WIFI_CONNECT_ATTEMPTS);
            if (WiFiConfig::instance().connect(
                    Config::WIFI_SSID,
                    Config::WIFI_PASSWORD,
                    Config::WIFI_CONNECT_TIMEOUT_MS
                )) {
                readyForUser_ = true;
                // Если пользователь уже коснулся Load во время подключения, сразу открываем список.
                if (Screen::Load::instance().continueRequested()) return new Idle();
                return this;
            }
        }

        // При провале Wi-Fi показываем экран с перезапуском и больше не переходим в Idle.
        Screen::Info::showRestart("WiFi недоступен", "Проверьте сеть и нажмите OK");
        wifiFailed_ = true;
        return this;
    }

    // После ошибки Wi-Fi остаемся в Boot, чтобы пользователь видел сообщение и мог перезапустить.
    if (wifiFailed_) return this;
    readyForUser_ = true;
    if (Screen::Load::instance().continueRequested()) return new Idle();
    return this;
}
