#pragma once

#include <ui/ui.h>

namespace Screen {

// Базовый класс страницы EEZ/LVGL с общей навигацией и жизненным циклом.
class Page {
public:
    // Связать страницу с идентификатором экрана из EEZ.
    explicit Page(ScreensEnum screenId);
    // Виртуальный деструктор нужен для корректной иерархии страниц.
    virtual ~Page() = default;

    // Показать страницу, подготовить обработчики и вызвать onShow().
    void show();
    // Скрыть страницу и вызвать onHide().
    void hide();
    // Вернуться на предыдущую страницу, если она известна.
    void back();

    // Выполнить onTick() активной страницы.
    static void process();
    // Вернуть активную страницу.
    static Page* activePage();
    // Вернуть страницу, с которой пришли на текущую.
    static Page* previousPage();
    // Восстановить previousPage; callOnShow управляет повторным onShow().
    static bool restorePrevious(bool callOnShow = true);
    // Перезагрузить активный EEZ-экран без смены активной страницы.
    static bool reloadActive(bool callOnShow = false);

protected:
    // Один раз вешает обработчики на EEZ-объекты.
    virtual void onPrepare() {}
    // Вызывается каждый раз при показе страницы.
    virtual void onShow() {}
    // Вызывается перед уходом со страницы.
    virtual void onHide() {}
    // Периодический tick активной страницы.
    virtual void onTick() {}

private:
    // Гарантирует однократный вызов onPrepare().
    void prepareOnce();

    // ID экрана, который нужно загрузить через loadScreen().
    ScreensEnum screenId_;
    // Флаг, что обработчики страницы уже привязаны.
    bool prepared_ = false;
    // Активная страница приложения.
    static Page* activePage_;
    // Предыдущая страница для простого back().
    static Page* previousPage_;
};

}  // namespace Screen
