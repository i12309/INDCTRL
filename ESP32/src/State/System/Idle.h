#pragma once

#include "State/State.h"

// Состояние ожидания пользователя после успешной загрузки.
class Idle : public State {
public:
    // Создать состояние ожидания.
    Idle();

protected:
    // Показать список работников при входе в Idle.
    void onEnter() override;
    // Оставаться в Idle, пока действия пользователя обрабатываются экранами.
    State* tick() override;
};
