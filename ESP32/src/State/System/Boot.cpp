#include "Boot.h"

#include <Arduino.h>

#include "Screen/Page/Main/Load.h"
#include "State/System/Idle.h"
#include "config.h"

Boot::Boot() : State(Type::Boot) {}

void Boot::onEnter() {
    startedAtMs_ = millis();
    Screen::Load::instance().setText("INDCTRL loading...");
    Screen::Load::instance().show();
}

State* Boot::tick() {
    if (millis() - startedAtMs_ < Config::BOOT_SCREEN_MS) return this;
    return new Idle();
}
