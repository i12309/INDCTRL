#pragma once

#include "Screen/Page/Page.h"

namespace Screen {

class Number : public Page {
public:
    static Number& instance();

protected:
    void onPrepare() override;
    void onShow() override;

private:
    Number();

    static void popDigit(lv_event_t* e);
    static void popBackspace(lv_event_t* e);
    static void popCancel(lv_event_t* e);
    static void popOk(lv_event_t* e);
    static void submit();
};

}  // namespace Screen
