#pragma once

#include "State/State.h"

class Boot : public State {
public:
    Boot();

protected:
    void onEnter() override;
    State* tick() override;

private:
    uint32_t startedAtMs_ = 0;
    bool wifiChecked_ = false;
    bool wifiFailed_ = false;
};
