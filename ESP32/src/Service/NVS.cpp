#include "NVS.h"

#include <nvs_flash.h>

#include "Service/Log.h"

NVS& NVS::instance() {
    static NVS nvs;
    return nvs;
}

bool NVS::begin() {
    esp_err_t err = nvs_flash_init();
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

bool NVS::setString(const char* key, const String& value, const char* ns) {
    if (!preferences_.begin(ns, false)) return false;
    const bool ok = preferences_.putString(key, value) > 0;
    preferences_.end();
    return ok;
}

String NVS::getString(const char* key, const String& fallback, const char* ns) {
    if (!preferences_.begin(ns, true)) return fallback;
    String value = preferences_.getString(key, fallback);
    preferences_.end();
    return value;
}

bool NVS::setInt(const char* key, int value, const char* ns) {
    if (!preferences_.begin(ns, false)) return false;
    const bool ok = preferences_.putInt(key, value) > 0;
    preferences_.end();
    return ok;
}

int NVS::getInt(const char* key, int fallback, const char* ns) {
    if (!preferences_.begin(ns, true)) return fallback;
    const int value = preferences_.getInt(key, fallback);
    preferences_.end();
    return value;
}

bool NVS::remove(const char* key, const char* ns) {
    if (!preferences_.begin(ns, false)) return false;
    const bool ok = preferences_.remove(key);
    preferences_.end();
    return ok;
}
