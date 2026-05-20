#include "Idle.h"

#include "Data.h"
#include "Screen/Page/Main/Load.h"
#include "Screen/Page/Main/Number.h"

Idle::Idle() : State(Type::Idle) {}

// При входе в Idle показываем экран ожидания.
void Idle::onEnter() {
    Data::runtime.clearSession();
    Screen::Load::instance().show();
}

// В Idle пользовательский тап по Load открывает ввод PIN.
State* Idle::tick() {
    if (Screen::Page::activePage() == &Screen::Load::instance() &&
        Screen::Load::instance().continueRequested()) {
        Screen::Number::instance().showLogin();
    }
    return this;
}
