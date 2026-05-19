#include "Error.h"

#include "Screen/Page/Main/Error.h"

ErrorState::ErrorState(const char* message) : State(Type::Error), message_(message) {}

void ErrorState::onEnter() {
    Screen::Error::show(message_);
}

State* ErrorState::tick() {
    return this;
}
