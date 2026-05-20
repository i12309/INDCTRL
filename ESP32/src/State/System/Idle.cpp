#include "Idle.h"

#include "Screen/Page/Main/List.h"

Idle::Idle() : State(Type::Idle) {}

// При входе в Idle показываем список работников.
void Idle::onEnter() {
    Screen::List::instance().show();
}

// Idle не меняет состояние сам; дальнейшая навигация идет через страницы.
State* Idle::tick() {
    return this;
}
