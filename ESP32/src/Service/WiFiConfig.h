#pragma once

#include <Arduino.h>
#include <WiFi.h>

// Сервис управления Wi-Fi подключением ESP32.
class WiFiConfig {
public:
    // Вернуть singleton Wi-Fi сервиса.
    static WiFiConfig& instance();

    // Перевести Wi-Fi в STA-режим.
    void init();
    // Подключиться к сети с таймаутом ожидания.
    bool connect(const char* ssid, const char* password, uint32_t timeoutMs = 10000);
    // Отключиться от текущей Wi-Fi сети.
    void disconnect();
    // Проверить, есть ли активное подключение.
    bool isConnected() const;
    // Вернуть SSID текущей сети.
    String ssid() const;
    // Вернуть локальный IP-адрес строкой.
    String ip() const;
    // Вернуть уровень RSSI в процентах 0..100.
    int rssiPercent() const;

private:
    // Запрещаем внешнее создание, чтобы управление Wi-Fi было централизованным.
    WiFiConfig() = default;
};
