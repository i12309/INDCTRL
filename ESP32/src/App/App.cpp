#include "App.h"

#include <Arduino.h>

#include "Screen/Panel/Panel.h"
#include "Service/Log.h"
#include "Service/Service.h"
#include "State/State.h"
#include "config.h"

App* App::instance_ = nullptr;

App::App() {
    instance_ = this;
}

App* App::instance() {
    return instance_;
}

App::Context& App::context() {
    return instance_->context_;
}

void App::init() {
    Log::init();
    Log::info("Starting %s", Config::APP_NAME);

    Service::init();
    Panel::init();
    State::init();

    context_.initialized = true;
}

void App::process() {
    Panel::process();
    State::process();
    Service::process();
    delay(Config::UI_TICK_DELAY_MS);
}
