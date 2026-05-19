#include "Service.h"

#include <WiFi.h>

#include "Data.h"
#include "Service/NVS.h"
#include "Service/WiFiConfig.h"

namespace {
ApiClient apiClient;
}

void Service::init() {
    NVS::instance().begin();
    WiFiConfig::instance().init();
    Data::runtime.deviceMac = WiFi.macAddress();
}

void Service::process() {}

ApiClient& Service::api() {
    return apiClient;
}
