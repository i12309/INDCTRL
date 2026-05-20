#pragma once

#include <Arduino.h>

namespace Config {
// Название приложения для логов и отображения.
inline constexpr const char* APP_NAME = "INDCTRL";
// Версия прошивки, выводится на экран Load.
inline constexpr const char* APP_VERSION = "0.1.0";
// Базовый адрес WEB API, к которому обращается ESP32.
inline constexpr const char* API_BASE_URL = "http://192.168.3.219";
// SSID Wi-Fi сети для подключения устройства.
inline constexpr const char* WIFI_SSID = "link";
// Пароль Wi-Fi сети.
inline constexpr const char* WIFI_PASSWORD = "!24865Pzekyxl!";
// Количество попыток подключения к Wi-Fi на этапе Boot.
inline constexpr uint8_t WIFI_CONNECT_ATTEMPTS = 3;
// Таймаут одной попытки подключения к Wi-Fi.
inline constexpr uint32_t WIFI_CONNECT_TIMEOUT_MS = 10000;
// Таймаут HTTP-запроса к WEB API.
inline constexpr uint32_t HTTP_REQUEST_TIMEOUT_MS = 7000;
// Интервал heartbeat текущей смены.
inline constexpr uint32_t HEARTBEAT_INTERVAL_MS = 60000;
// Пауза основного цикла UI, чтобы LVGL и тач не перегружали CPU.
inline constexpr uint32_t UI_TICK_DELAY_MS = 5;
// Минимальное время показа Load перед проверкой Wi-Fi.
inline constexpr uint32_t BOOT_SCREEN_MS = 800;
}
