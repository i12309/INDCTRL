#include "Service.h"

#include <WiFi.h>

#include "Data.h"
#include "Service/DeviceApi.h"
#include "Service/Log.h"
#include "Service/NVS.h"
#include "Service/WiFiConfig.h"
#include "config.h"

namespace {
ApiClient apiClient;
uint32_t lastHeartbeatMs = 0;
}

void Service::init() {
    NVS::instance().begin();
    WiFiConfig::instance().init();
    Data::runtime.deviceMac = WiFi.macAddress();
}

void Service::process() {
    if (Data::runtime.sessionId.length() == 0) {
        lastHeartbeatMs = 0;
        return;
    }

    const uint32_t now = millis();
    if (lastHeartbeatMs == 0) {
        lastHeartbeatMs = now;
        return;
    }

    if (now - lastHeartbeatMs < Config::HEARTBEAT_INTERVAL_MS) return;
    lastHeartbeatMs = now;

    ApiResult result = DeviceApi::heartbeat(Data::runtime.sessionId);
    if (!result.success) {
        Log::error("Heartbeat failed: %s", result.error.c_str());
    }
}

ApiClient& Service::api() {
    return apiClient;
}
