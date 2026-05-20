#include "Wait.h"

#include <Arduino.h>

#include "Screen/Page/Main/Load.h"
#include "Screen/Panel/LvglHelpers.h"
#include "Screen/Panel/Panel.h"

#include <ui/screens.h>
#include <lvgl/lvgl.h>

namespace Screen {

namespace {
// Заголовок Wait по умолчанию.
constexpr const char* DEFAULT_TITLE = "Подождите";

// Минимальное время видимости Wait, чтобы короткие запросы не мигали.
constexpr uint32_t MIN_VISIBLE_MS = 250;
// Флаг, что Wait сейчас подменяет активный экран.
bool waitVisible = false;

// Принудительно перерисовать LVGL после показа/скрытия Wait.
void refreshUi() {
    if (!Panel::isInitialized()) return;
    lv_refr_now(nullptr);
    delay(20);
    lv_refr_now(nullptr);
}
}  // namespace

Wait::Wait() : Page(SCREEN_ID_WAIT) {}

// Вернуть singleton страницы.
Wait& Wait::instance() {
    static Wait page;
    return page;
}

// Показать Wait поверх текущей страницы без смены Page::activePage_.
void Wait::show(const char* title) {
    Wait& page = instance();
    page.setTitle(title);
    loadScreen(SCREEN_ID_WAIT);
    page.onShow();
    waitVisible = true;
}

// Закрыть Wait и перезагрузить активный экран.
void Wait::dismiss() {
    // Если Wait не был показан, повторное закрытие игнорируем.
    if (!waitVisible) return;
    waitVisible = false;
    (void)Page::reloadActive(false);
}

// Установить заголовок ожидания.
void Wait::setTitle(const char* title) {
    title_ = title == nullptr || title[0] == '\0' ? DEFAULT_TITLE : title;
}

// Заполнить поля Wait при показе.
void Wait::onShow() {
    Ui::setText(objects.wait_title, title_);
    Ui::setText(objects.wait_field1, "");
    Ui::setText(objects.wait_field3, "");
}

// Создать guard и при необходимости показать Wait.
WaitGuard::WaitGuard(const char* title) {
    // Пустой title означает, что вызывающий код не хочет показывать Wait.
    if (title == nullptr || title[0] == '\0') return;
    // До инициализации панели показывать экран невозможно.
    if (!Panel::isInitialized()) return;
    // На Load не показываем Wait, чтобы заставка не сменялась сама.
    if (Page::activePage() == nullptr || Page::activePage() == &Load::instance()) return;

    Wait::show(title);
    active_ = true;
    startedAtMs_ = millis();
    refreshUi();
}

// Скрыть Wait и выдержать минимальную длительность показа.
WaitGuard::~WaitGuard() {
    if (!active_) return;
    const uint32_t elapsed = millis() - startedAtMs_;
    // Если запрос завершился слишком быстро, держим Wait чуть дольше для плавности UI.
    if (elapsed < MIN_VISIBLE_MS) delay(MIN_VISIBLE_MS - elapsed);

    Wait::dismiss();
    refreshUi();
}

}  // namespace Screen
