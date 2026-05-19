#pragma once

#include <Arduino.h>
#include <Preferences.h>

class NVS {
public:
    static NVS& instance();

    bool begin();
    bool setString(const char* key, const String& value, const char* ns = "indctrl");
    String getString(const char* key, const String& fallback = "", const char* ns = "indctrl");
    bool setInt(const char* key, int value, const char* ns = "indctrl");
    int getInt(const char* key, int fallback = 0, const char* ns = "indctrl");
    bool remove(const char* key, const char* ns = "indctrl");

private:
    NVS() = default;
    Preferences preferences_;
};
