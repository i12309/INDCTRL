#pragma once

#include <Arduino.h>

#include "Screen/Page/Page.h"

namespace Screen {

class Wait : public Page {
public:
    static Wait& instance();
    static void show(const char* title);
    static void dismiss();

    void setTitle(const char* title);

protected:
    void onShow() override;

private:
    Wait();
    String title_ = "Подождите";
};

class WaitGuard {
public:
    explicit WaitGuard(const char* title);
    ~WaitGuard();

    WaitGuard(const WaitGuard&) = delete;
    WaitGuard& operator=(const WaitGuard&) = delete;

private:
    bool active_ = false;
    uint32_t startedAtMs_ = 0;
};

}
