#include "NVS.h"

#include <nvs_flash.h>

#include "Service/Log.h"

// Вернуть singleton NVS.
NVS& NVS::instance() {
    static NVS nvs;
    return nvs;
}

// Инициализировать flash-хранилище ESP32.
bool NVS::begin() {
    esp_err_t err = nvs_flash_init();
    // При несовместимой версии или заполненных страницах NVS нужно стереть и переинициализировать.
    if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        err = nvs_flash_init();
    }
    if (err != ESP_OK) {
        Log::error("NVS init failed: %d", static_cast<int>(err));
        return false;
    }
    return true;
}

// Сохранить строковое значение.
bool NVS::setString(const char* key, const String& value, const char* ns) {
    if (!preferences_.begin(ns, false)) return false;
    const bool ok = preferences_.putString(key, value) > 0;
    preferences_.end();
    return ok;
}

// Прочитать строковое значение.
String NVS::getString(const char* key, const String& fallback, const char* ns) {
    if (!preferences_.begin(ns, true)) return fallback;
    String value = preferences_.getString(key, fallback);
    preferences_.end();
    return value;
}

// Сохранить целое значение.
bool NVS::setInt(const char* key, int value, const char* ns) {
    if (!preferences_.begin(ns, false)) return false;
    const bool ok = preferences_.putInt(key, value) > 0;
    preferences_.end();
    return ok;
}

// Прочитать целое значение.
int NVS::getInt(const char* key, int fallback, const char* ns) {
    if (!preferences_.begin(ns, true)) return fallback;
    const int value = preferences_.getInt(key, fallback);
    preferences_.end();
    return value;
}

// Удалить ключ из namespace.
bool NVS::remove(const char* key, const char* ns) {
    if (!preferences_.begin(ns, false)) return false;
    const bool ok = preferences_.remove(key);
    preferences_.end();
    return ok;
}
