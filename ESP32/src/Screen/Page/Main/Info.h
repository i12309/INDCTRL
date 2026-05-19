#pragma once

#include <Arduino.h>

#include "Screen/Page/Page.h"

namespace Screen {

class Info : public Page {
public:
    static Info& instance();
    static void showInfo(const char* title, const char* message);
    static void showInfo(const char* title, const char* message, const char* detail);
    static void showRestart(const char* title, const char* message);
    static void showRestart(const char* title, const char* message, const char* detail);

protected:
    void onPrepare() override;
    void onShow() override;

private:
    Info();
    void render();

    static void popOk(lv_event_t* e);

    String title_ = "Info";
    String message_;
    String detail_;
    bool restartOnOk_ = false;
};

}  // namespace Screen
