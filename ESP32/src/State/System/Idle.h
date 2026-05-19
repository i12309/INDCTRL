#pragma once

#include "State/State.h"

class Idle : public State {
public:
    Idle();

protected:
    void onEnter() override;
    State* tick() override;
};
