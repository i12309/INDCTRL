#pragma once

#include "State/State.h"

class WorkProcess : public State {
public:
    WorkProcess();

protected:
    void onEnter() override;
    State* tick() override;
};
