#pragma once

#include <cstddef>

#include "Screen/Page/Page.h"

namespace Screen {

// Страница выбора работника для входа в смену.
class List : public Page {
public:
    // Вернуть singleton страницы List.
    static List& instance();

protected:
    // Привязать кнопки листания и строки работников.
    void onPrepare() override;
    // При показе загрузить работников и отрисовать первую страницу.
    void onShow() override;

private:
    // Создать страницу и связать ее с EEZ SCREEN_ID_LIST.
    List();
    // Загрузить работников для текущего MAC-адреса.
    bool loadWorkers();
    // Отрисовать видимые 6 строк и кнопки листания.
    void render();

    // Перейти на предыдущую страницу работников.
    static void popBack(lv_event_t* e);
    // Перейти на следующую страницу работников.
    static void popNext(lv_event_t* e);
    // Выбрать работника из строки и открыть ввод PIN.
    static void popItem(lv_event_t* e);

    // Смещение первого работника на текущей странице.
    size_t offset_ = 0;
};

}  // namespace Screen
