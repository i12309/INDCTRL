#include "Load.h"

#include "Data.h"
#include "Screen/Panel/LvglHelpers.h"
#include "config.h"

#include <ui/screens.h>

namespace Screen {

Load::Load() : Page(SCREEN_ID_LOAD) {}

// Вернуть singleton страницы.
Load& Load::instance() {
    static Load page;
    return page;
}

// Вернуть флаг касания экрана Load.
bool Load::continueRequested() const {
    return continueRequested_;
}

// Сохранить текст загрузки для совместимости со старым API страницы.
void Load::setText(const char* text) {
    text_ = text == nullptr ? "Loading..." : text;
    (void)text_;
}

// Привязать касание ко всем видимым зонам Load.
void Load::onPrepare() {
    registerContinueTarget(objects.load);
    registerContinueTarget(objects.obj8);
    registerContinueTarget(objects.obj9);
    registerContinueTarget(objects.obj10);
    registerContinueTarget(objects.obj11);
    registerContinueTarget(objects.load_ma_caddress);
    registerContinueTarget(objects.load_version);
}

// Вывести MAC и версию, а также сбросить касание при новом показе Load.
void Load::onShow() {
    continueRequested_ = false;
    Ui::setText(objects.load_ma_caddress, Data::runtime.deviceMac);
    Ui::setText(objects.load_version, Config::APP_VERSION);
}

// Отметить, что пользователь просит перейти дальше после загрузки.
void Load::popContinue(lv_event_t* e) {
    (void)e;
    instance().continueRequested_ = true;
}

// Сделать объект кликабельным и подписать его на касание.
void Load::registerContinueTarget(lv_obj_t* obj) {
    // Некоторые объекты могут отсутствовать, если EEZ-проект изменится.
    if (obj == nullptr) return;

    lv_obj_add_flag(obj, LV_OBJ_FLAG_CLICKABLE);
    lv_obj_add_event_cb(obj, Load::popContinue, LV_EVENT_PRESSED, nullptr);
}

}  // namespace Screen
