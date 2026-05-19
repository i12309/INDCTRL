#pragma once

#include "Screen/Page/Page.h"

namespace Screen {

class Info : public Page {
public:
    static Info& instance();
    static void showInfo(const char* title, const char* message);

protected:
    void onPrepare() override;
    void onShow() override;

private:
    Info();
    void render();

    static void popOk(lv_event_t* e);

    const char* title_ = "Info";
    const char* message_ = "";
};

}  // namespace Screen
