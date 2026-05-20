#include "Error.h"

#include "Screen/Page/Main/Error.h"

ErrorState::ErrorState(const char* message) : State(Type::Error), message_(message) {}

// Показать переданный текст ошибки.
void ErrorState::onEnter() {
    Screen::Error::show(message_);
}

// Состояние ошибки не переключается автоматически.
State* ErrorState::tick() {
    return this;
}
