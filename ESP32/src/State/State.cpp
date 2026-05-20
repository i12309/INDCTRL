#include "State.h"

#include "State/System/Boot.h"

State* State::current_ = nullptr;

// Запустить машину состояний с Boot.
void State::init() {
    set(new Boot());
}

// Выполнить tick текущего состояния и применить переход, если он вернул новый объект.
void State::process() {
    if (current_ == nullptr) return;
    State* next = current_->tick();
    if (next != nullptr && next != current_) set(next);
}

// Заменить активное состояние; старое удаляется, чтобы не было утечки памяти.
void State::set(State* next) {
    // Игнорируем пустой переход и переход в тот же объект.
    if (next == nullptr || next == current_) return;
    delete current_;
    current_ = next;
    current_->onEnter();
}

// Вернуть текущее состояние для диагностики или внешней проверки.
State* State::current() {
    return current_;
}
