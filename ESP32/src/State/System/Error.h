#pragma once

#include "State/State.h"

// Системное состояние ошибки, показывающее сообщение на UI.
class ErrorState : public State {
public:
    // Создать ошибку с текстом для пользователя.
    explicit ErrorState(const char* message);

protected:
    // Показать экран ошибки.
    void onEnter() override;
    // Оставаться в ошибке до перезапуска или внешнего переключения состояния.
    State* tick() override;

private:
    // Текст ошибки, который передается на экран Info.
    const char* message_;
};
