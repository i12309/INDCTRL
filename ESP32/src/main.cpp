#include <Arduino.h>

#include "App/App.h"

namespace {
// Глобальный App нужен Arduino-циклу, чтобы объект жил все время работы прошивки.
App app;
}

// Точка входа Arduino: инициализирует приложение один раз после старта ESP32.
void setup() {
    app.init();
}

// Основной цикл Arduino: передает управление приложению.
void loop() {
    app.process();
}
