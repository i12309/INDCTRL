#pragma once

#include "Screen/Page/Main/Load.h"

namespace Screen {

// Совместимый фасад старого экрана инициализации.
class INIT {
public:
    // Показать Load с текстом инициализации.
    static void show() {
        Load::instance().setText("Initializing...");
        Load::instance().show();
    }
};

}  // namespace Screen
