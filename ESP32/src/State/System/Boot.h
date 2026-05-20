#pragma once

#include "State/State.h"

// Состояние загрузки: показывает Load, проверяет Wi-Fi и ждет касания пользователя.
class Boot : public State {
public:
    // Создать состояние Boot.
    Boot();

protected:
    // Запомнить время старта и показать экран Load.
    void onEnter() override;
    // Проверить задержку, подключить Wi-Fi и дождаться касания Load перед List.
    State* tick() override;

private:
    // Время входа в Boot, нужно для минимального показа Load.
    uint32_t startedAtMs_ = 0;
    // Флаг, что попытки подключения к Wi-Fi уже выполнялись.
    bool wifiChecked_ = false;
    // Флаг ошибки Wi-Fi; после него остаемся на экране ошибки/Load.
    bool wifiFailed_ = false;
    // Wi-Fi готов, но List еще не показан, пока пользователь не коснется Load.
    bool readyForUser_ = false;
};
