#pragma once

#include <Arduino.h>

#include "Screen/Page/Page.h"

namespace Screen {

// Страница ожидания, показываемая во время сетевых запросов.
class Wait : public Page {
public:
    // Вернуть singleton страницы Wait.
    static Wait& instance();
    // Показать Wait с заголовком.
    static void show(const char* title);
    // Закрыть Wait и восстановить предыдущий экран.
    static void dismiss();

    // Изменить заголовок уже существующего Wait.
    void setTitle(const char* title);

protected:
    // Вывести текущий заголовок ожидания.
    void onShow() override;

private:
    // Создать страницу и связать ее с EEZ SCREEN_ID_WAIT.
    Wait();
    // Заголовок, отображаемый на экране ожидания.
    String title_ = "Подождите";
};

// RAII-обертка: показывает Wait на время блока и скрывает в деструкторе.
class WaitGuard {
public:
    // Показать Wait и запомнить время старта.
    explicit WaitGuard(const char* title);
    // Закрыть Wait, если он был реально показан.
    ~WaitGuard();

    // Копирование запрещено, чтобы один WaitGuard не закрывался дважды.
    WaitGuard(const WaitGuard&) = delete;
    // Присваивание запрещено по той же причине, что и копирование.
    WaitGuard& operator=(const WaitGuard&) = delete;

private:
    // true, если деструктор должен закрыть Wait.
    bool active_ = false;
    // Время создания guard, чтобы короткие запросы не мигали экраном.
    uint32_t startedAtMs_ = 0;
};

}
