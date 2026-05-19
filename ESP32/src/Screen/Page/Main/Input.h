#pragma once

#include "Screen/Page/Main/Info.h"

namespace Screen {

class Input {
public:
    static void showPlaceholder() {
        Info::showInfo("Input", "Input page placeholder");
    }
};

}  // namespace Screen
