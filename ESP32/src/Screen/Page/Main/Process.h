#pragma once

#include "Screen/Page/Page.h"

namespace Screen {

// Основная страница активной смены: счетчик, статус, детали и закрытие.
class Process : public Page {
public:
    // Вернуть singleton страницы Process.
    static Process& instance();

protected:
    // Привязать кнопки деталей и закрытия смены.
    void onPrepare() override;
    // Перерисовать данные смены при показе.
    void onShow() override;

private:
    // Создать страницу и связать ее с EEZ SCREEN_ID_PROCESS.
    Process();
    // Вывести номер смены, ФИО, максимальный номер детали и последний статус.
    void render();

    // Открыть страницу деталей.
    static void popDetails(lv_event_t* e);
    // Открыть PIN-подтверждение закрытия смены.
    static void popClose(lv_event_t* e);
};

}  // namespace Screen
