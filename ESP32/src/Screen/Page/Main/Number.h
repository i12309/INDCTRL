#pragma once

#include <Arduino.h>

#include "Screen/Page/Page.h"

namespace Screen {

class Number : public Page {
public:
    static Number& instance();
    void showLogin();
    void showCloseShift();

protected:
    void onPrepare() override;
    void onShow() override;

private:
    enum class Mode {
        Login,
        CloseShift,
    };

    Number();

    static void popDigit(lv_event_t* e);
    static void popBackspace(lv_event_t* e);
    static void popCancel(lv_event_t* e);
    static void popOk(lv_event_t* e);
    static void submit();
    void submitLogin(const String& password);
    void submitCloseShift(const String& password);

    Mode mode_ = Mode::Login;
};

}  // namespace Screen
