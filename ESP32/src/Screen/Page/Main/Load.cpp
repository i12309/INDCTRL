#include "Load.h"

#include "Data.h"
#include "Screen/Panel/LvglHelpers.h"
#include "config.h"

#include <ui/screens.h>

namespace Screen {

Load::Load() : Page(SCREEN_ID_LOAD) {}

Load& Load::instance() {
    static Load page;
    return page;
}

bool Load::continueRequested() const {
    return continueRequested_;
}

void Load::setText(const char* text) {
    text_ = text == nullptr ? "Loading..." : text;
    (void)text_;
}

void Load::onPrepare() {
    registerContinueTarget(objects.load);
    registerContinueTarget(objects.obj8);
    registerContinueTarget(objects.obj9);
    registerContinueTarget(objects.obj10);
    registerContinueTarget(objects.obj11);
    registerContinueTarget(objects.load_ma_caddress);
    registerContinueTarget(objects.load_version);
}

void Load::onShow() {
    continueRequested_ = false;
    Ui::setText(objects.load_ma_caddress, Data::runtime.deviceMac);
    Ui::setText(objects.load_version, Config::APP_VERSION);
}

void Load::popContinue(lv_event_t* e) {
    (void)e;
    instance().continueRequested_ = true;
}

void Load::registerContinueTarget(lv_obj_t* obj) {
    if (obj == nullptr) return;

    lv_obj_add_flag(obj, LV_OBJ_FLAG_CLICKABLE);
    lv_obj_add_event_cb(obj, Load::popContinue, LV_EVENT_PRESSED, nullptr);
}

}  // namespace Screen
