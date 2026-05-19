#include "Idle.h"

#include "Screen/Page/Main/List.h"

Idle::Idle() : State(Type::Idle) {}

void Idle::onEnter() {
    Screen::List::instance().show();
}

State* Idle::tick() {
    return this;
}
