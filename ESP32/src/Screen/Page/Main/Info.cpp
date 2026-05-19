#include "Info.h"

#include <Arduino.h>

#include "Screen/Panel/LvglHelpers.h"

#include <ui/screens.h>

namespace Screen {

Info::Info() : Page(SCREEN_ID_INFO) {}

Info& Info::instance() {
    static Info page;
    return page;
}

void Info::showInfo(const char* title, const char* message) {
    showInfo(title, message, "");
}

void Info::showInfo(const char* title, const char* message, const char* detail) {
    Info& page = instance();
    page.title_ = title == nullptr ? "Info" : title;
    page.message_ = message == nullptr ? "" : message;
    page.detail_ = detail == nullptr ? "" : detail;
    page.restartOnOk_ = false;
    page.show();
    page.render();
}

void Info::showRestart(const char* title, const char* message) {
    showRestart(title, message, "");
}

void Info::showRestart(const char* title, const char* message, const char* detail) {
    Info& page = instance();
    page.title_ = title == nullptr ? "Info" : title;
    page.message_ = message == nullptr ? "" : message;
    page.detail_ = detail == nullptr ? "" : detail;
    page.restartOnOk_ = true;
    page.show();
    page.render();
}

void Info::onPrepare() {
    Ui::onPop(objects.info_ok, Info::popOk);
    Ui::onPop(objects.info_back, Info::popOk);
}

void Info::onShow() {
    render();
}

void Info::render() {
    Ui::setText(objects.info_field1, title_);
    Ui::setText(objects.info_field2, message_);
    Ui::setText(objects.info_field3, detail_);
    Ui::setText(objects.info_ok, "OK");
    Ui::setHidden(objects.info_next, true);
}

void Info::popOk(lv_event_t* e) {
    (void)e;
    if (instance().restartOnOk_) {
        ESP.restart();
        return;
    }
    instance().back();
}

}  // namespace Screen
