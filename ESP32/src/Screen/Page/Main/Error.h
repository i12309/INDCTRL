#pragma once

#include "Screen/Page/Main/Info.h"

namespace Screen {

class Error {
public:
    static void show(const char* message) {
        Info::showInfo("Error", message);
    }
};

}  // namespace Screen
