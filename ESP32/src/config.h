#pragma once

#include <Arduino.h>

namespace Config {
inline constexpr const char* APP_NAME = "INDCTRL";
inline constexpr const char* APP_VERSION = "0.1.0";
inline constexpr const char* API_BASE_URL = "http://localhost";
inline constexpr uint32_t UI_TICK_DELAY_MS = 5;
inline constexpr uint32_t BOOT_SCREEN_MS = 800;
}
