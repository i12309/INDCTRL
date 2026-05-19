#pragma once

#include <Arduino.h>

namespace Config {
inline constexpr const char* APP_NAME = "INDCTRL";
inline constexpr const char* APP_VERSION = "0.1.0";
inline constexpr const char* API_BASE_URL = "http://192.168.3.219";
inline constexpr const char* WIFI_SSID = "link";
inline constexpr const char* WIFI_PASSWORD = "!24865Pzekyxl!";
inline constexpr uint8_t WIFI_CONNECT_ATTEMPTS = 3;
inline constexpr uint32_t WIFI_CONNECT_TIMEOUT_MS = 10000;
inline constexpr uint32_t HTTP_REQUEST_TIMEOUT_MS = 7000;
inline constexpr uint32_t UI_TICK_DELAY_MS = 5;
inline constexpr uint32_t BOOT_SCREEN_MS = 800;
}
