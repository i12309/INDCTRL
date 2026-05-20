#include "Service.h"

#include <WiFi.h>

#include "Data.h"
#include "Service/DeviceApi.h"
#include "Service/Log.h"
#include "Service/NVS.h"
#include "Service/WiFiConfig.h"
#include "config.h"

namespace {
// Общий HTTP-клиент для всех бизнес-запросов устройства.
ApiClient apiClient;
// Время последней отправки heartbeat текущей сессии.
uint32_t lastHeartbeatMs = 0;
}

// Инициализировать постоянное хранилище, Wi-Fi режим и MAC-адрес runtime.
void Service::init() {
    NVS::instance().begin();
    WiFiConfig::instance().init();
    Data::runtime.deviceMac = WiFi.macAddress();
}

// Обслужить фоновые задачи сервисного слоя.
void Service::process() {
    // Если смена не открыта, heartbeat не нужен, а таймер надо сбросить для будущей сессии.
    if (Data::runtime.sessionId.length() == 0) {
        lastHeartbeatMs = 0;
        return;
    }

    const uint32_t now = millis();
    // Первый проход после login только стартует интервал, чтобы не слать heartbeat сразу после login.
    if (lastHeartbeatMs == 0) {
        lastHeartbeatMs = now;
        return;
    }

    // Пока интервал не прошел, не создаем лишний сетевой трафик.
    if (now - lastHeartbeatMs < Config::HEARTBEAT_INTERVAL_MS) return;
    lastHeartbeatMs = now;

    ApiResult result = DeviceApi::heartbeat(Data::runtime.sessionId);
    // Ошибка heartbeat не закрывает смену локально, только пишется в лог.
    if (!result.success) {
        Log::error("Heartbeat failed: %s", result.error.c_str());
    }
}

// Вернуть общий API-клиент.
ApiClient& Service::api() {
    return apiClient;
}
