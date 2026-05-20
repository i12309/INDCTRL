#pragma once

#include <Arduino.h>
#include <Preferences.h>

// Обертка над Preferences/NVS для постоянных настроек ESP32.
class NVS {
public:
    // Вернуть singleton хранилища.
    static NVS& instance();

    // Проверить доступность NVS, открыв и закрыв namespace.
    bool begin();
    // Сохранить строку по ключу в namespace.
    bool setString(const char* key, const String& value, const char* ns = "indctrl");
    // Прочитать строку по ключу или вернуть fallback.
    String getString(const char* key, const String& fallback = "", const char* ns = "indctrl");
    // Сохранить целое число по ключу.
    bool setInt(const char* key, int value, const char* ns = "indctrl");
    // Прочитать целое число по ключу или вернуть fallback.
    int getInt(const char* key, int fallback = 0, const char* ns = "indctrl");
    // Удалить ключ из namespace.
    bool remove(const char* key, const char* ns = "indctrl");

private:
    // Запрещаем внешнее создание, чтобы не плодить Preferences.
    NVS() = default;
    // Низкоуровневый объект ESP32 Preferences.
    Preferences preferences_;
};
