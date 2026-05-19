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

void Load::setText(const char* text) {
    text_ = text == nullptr ? "Loading..." : text;
    (void)text_;
}

void Load::onShow() {
    Ui::setText(objects.load_ma_caddress, Data::runtime.deviceMac);
    Ui::setText(objects.load_version, Config::APP_VERSION);
}

}  // namespace Screen
