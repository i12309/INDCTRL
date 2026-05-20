#include "App.h"

#include <Arduino.h>

#include "Screen/Panel/Panel.h"
#include "Service/Log.h"
#include "Service/Service.h"
#include "State/State.h"
#include "config.h"

App* App::instance_ = nullptr;

// Регистрирует текущий объект как singleton приложения.
App::App() {
    instance_ = this;
}

// Возвращает singleton приложения для Arduino loop и других слоев.
App* App::instance() {
    return instance_;
}

// Возвращает общий контекст приложения.
App::Context& App::context() {
    return instance_->context_;
}

// Инициализирует логирование, сервисы, UI и машину состояний.
void App::init() {
    Log::init();
    Log::info("Starting %s", Config::APP_NAME);

    Service::init();
    Panel::init();
    State::init();

    context_.initialized = true;
}

// Выполняет один цикл UI, состояний и сервисов.
void App::process() {
    // Сначала обслуживаем LVGL, затем бизнес-состояния, затем фоновые сервисы.
    Panel::process();
    State::process();
    Service::process();
    delay(Config::UI_TICK_DELAY_MS);
}
