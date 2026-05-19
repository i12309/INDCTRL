#include "State.h"

#include "State/System/Boot.h"

State* State::current_ = nullptr;

void State::init() {
    set(new Boot());
}

void State::process() {
    if (current_ == nullptr) return;
    State* next = current_->tick();
    if (next != nullptr && next != current_) set(next);
}

void State::set(State* next) {
    if (next == nullptr || next == current_) return;
    delete current_;
    current_ = next;
    current_->onEnter();
}

State* State::current() {
    return current_;
}
