#pragma once

#include "Screen/Page/Main/Load.h"

namespace Screen {

class INIT {
public:
    static void show() {
        Load::instance().setText("Initializing...");
        Load::instance().show();
    }
};

}  // namespace Screen
