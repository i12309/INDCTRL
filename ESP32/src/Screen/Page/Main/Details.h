#pragma once

#include <cstddef>

#include "Screen/Page/Page.h"

namespace Screen {

// Страница списка деталей текущей смены.
class Details : public Page {
public:
    // Вернуть singleton страницы Details.
    static Details& instance();

protected:
    // Привязать кнопки листания.
    void onPrepare() override;
    // При показе загрузить детали и отрисовать текущую страницу.
    void onShow() override;

private:
    // Создать страницу и связать ее с EEZ SCREEN_ID_DETAILS.
    Details();
    // Загрузить детали текущей смены с сервера.
    void loadDetails();
    // Отрисовать текущие 6 строк деталей.
    void render();

    // Обработать кнопку назад: листание назад или возврат на Process.
    static void popBack(lv_event_t* e);
    // Обработать кнопку вперед по страницам деталей.
    static void popNext(lv_event_t* e);

    // Смещение первой детали на текущей странице.
    size_t offset_ = 0;
};

}  // namespace Screen
