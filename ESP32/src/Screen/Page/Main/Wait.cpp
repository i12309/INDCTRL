#include "Wait.h"

#include <Arduino.h>

#include "Screen/Page/Main/Load.h"
#include "Screen/Panel/LvglHelpers.h"
#include "Screen/Panel/Panel.h"

#include <ui/screens.h>
#include <lvgl/lvgl.h>

namespace Screen {

namespace {
constexpr const char* DEFAULT_TITLE = "Подождите";

constexpr uint32_t MIN_VISIBLE_MS = 250;
bool waitVisible = false;

void refreshUi() {
    if (!Panel::isInitialized()) return;
    lv_refr_now(nullptr);
    delay(20);
    lv_refr_now(nullptr);
}
}  // namespace

Wait::Wait() : Page(SCREEN_ID_WAIT) {}

Wait& Wait::instance() {
    static Wait page;
    return page;
}

void Wait::show(const char* title) {
    Wait& page = instance();
    page.setTitle(title);
    loadScreen(SCREEN_ID_WAIT);
    page.onShow();
    waitVisible = true;
}

void Wait::dismiss() {
    if (!waitVisible) return;
    waitVisible = false;
    (void)Page::reloadActive(false);
}

void Wait::setTitle(const char* title) {
    title_ = title == nullptr || title[0] == '\0' ? DEFAULT_TITLE : title;
}

void Wait::onShow() {
    Ui::setText(objects.wait_title, title_);
    Ui::setText(objects.wait_field1, "");
    Ui::setText(objects.wait_field3, "");
}

WaitGuard::WaitGuard(const char* title) {
    if (!Panel::isInitialized()) return;
    if (Page::activePage() == nullptr || Page::activePage() == &Load::instance()) return;

    Wait::show(title);
    active_ = true;
    startedAtMs_ = millis();
    refreshUi();
}

WaitGuard::~WaitGuard() {
    if (!active_) return;
    const uint32_t elapsed = millis() - startedAtMs_;
    if (elapsed < MIN_VISIBLE_MS) delay(MIN_VISIBLE_MS - elapsed);

    Wait::dismiss();
    refreshUi();
}

}  // namespace Screen
