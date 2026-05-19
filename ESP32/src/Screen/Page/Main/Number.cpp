#include "Number.h"

#include "Data.h"
#include "Screen/Page/Main/Info.h"
#include "Screen/Page/Main/Process.h"
#include "Screen/Panel/LvglHelpers.h"
#include "Service/DeviceApi.h"

#include <ui/screens.h>

namespace Screen {

Number::Number() : Page(SCREEN_ID_NUMBER) {}

Number& Number::instance() {
    static Number page;
    return page;
}

void Number::onPrepare() {
    Ui::onPop(objects.kbd_0, Number::popDigit, (void*)"0");
    Ui::onPop(objects.kbd_1, Number::popDigit, (void*)"1");
    Ui::onPop(objects.kbd_2, Number::popDigit, (void*)"2");
    Ui::onPop(objects.kbd_3, Number::popDigit, (void*)"3");
    Ui::onPop(objects.kbd_4, Number::popDigit, (void*)"4");
    Ui::onPop(objects.kbd_5, Number::popDigit, (void*)"5");
    Ui::onPop(objects.kbd_6, Number::popDigit, (void*)"6");
    Ui::onPop(objects.kbd_7, Number::popDigit, (void*)"7");
    Ui::onPop(objects.kbd_8, Number::popDigit, (void*)"8");
    Ui::onPop(objects.kbd_9, Number::popDigit, (void*)"9");
    Ui::onPop(objects.kbd_backspace, Number::popBackspace);
    Ui::onPop(objects.kbd_cancel, Number::popCancel);
    Ui::onPop(objects.kbd_ok, Number::popOk);
}

void Number::onShow() {
    Ui::setText(objects.kbd_text, "");
}

void Number::popDigit(lv_event_t* e) {
    const char* digit = static_cast<const char*>(lv_event_get_user_data(e));
    if (digit == nullptr) return;

    String value = Ui::getText(objects.kbd_text);
    if (value.length() >= 32) return;
    value += digit;
    Ui::setText(objects.kbd_text, value);
}

void Number::popBackspace(lv_event_t* e) {
    (void)e;
    String value = Ui::getText(objects.kbd_text);
    if (value.length() == 0) return;
    value.remove(value.length() - 1);
    Ui::setText(objects.kbd_text, value);
}

void Number::popCancel(lv_event_t* e) {
    (void)e;
    instance().back();
}

void Number::popOk(lv_event_t* e) {
    (void)e;
    submit();
}

void Number::submit() {
    String password = Ui::getText(objects.kbd_text);
    password.trim();
    if (password.length() == 0) return;

    LoginResult result = DeviceApi::login(Data::runtime.userId, password, Data::runtime.deviceMac);
    if (!result.success) {
        Ui::setText(objects.kbd_text, "");
        if (result.error.indexOf("занят") >= 0) {
            Info::showRestart("Ошибка входа", result.error.c_str());
            return;
        }

        Info::showInfo("Ошибка входа", result.error.c_str());
        return;
    }

    Data::runtime.sessionId = result.sessionId;
    Data::runtime.userId = result.userId;
    Data::runtime.machineId = result.machineId;
    Data::runtime.workId = result.workId;
    Process::instance().show();
}

}  // namespace Screen
