#include "Process.h"

#include "Screen/Page/Main/Process.h"

WorkProcess::WorkProcess() : State(Type::Process) {}

void WorkProcess::onEnter() {
    Screen::Process::instance().show();
}

State* WorkProcess::tick() {
    return this;
}
