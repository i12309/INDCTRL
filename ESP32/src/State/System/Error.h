#pragma once

#include "State/State.h"

class ErrorState : public State {
public:
    explicit ErrorState(const char* message);

protected:
    void onEnter() override;
    State* tick() override;

private:
    const char* message_;
};
