#include "Panel.h"

#include <Arduino.h>
#include <esp32_smartdisplay.h>
#include <lvgl/lvgl.h>
#include <ui/ui.h>

namespace {
// true после успешной инициализации smartdisplay и EEZ UI.
bool initialized = false;
// Последнее время обновления lv_tick_inc().
uint32_t lastTickMs = 0;
}

// Инициализировать дисплей, подсветку и EEZ UI.
void Panel::init() {
    // Повторная инициализация LVGL/дисплея опасна, поэтому сразу выходим.
    if (initialized) return;

    smartdisplay_init();
    smartdisplay_lcd_set_backlight(1.0f);
    ui_init();

    lastTickMs = millis();
    initialized = true;
}

// Обработать LVGL timers и EEZ tick.
void Panel::process() {
    if (!initialized) return;

    // LVGL требует монотонного приращения tick между вызовами timer_handler().
    const uint32_t now = millis();
    lv_tick_inc(now - lastTickMs);
    lastTickMs = now;

    lv_timer_handler();
    ui_tick();
}

// Вернуть флаг готовности панели.
bool Panel::isInitialized() {
    return initialized;
}
