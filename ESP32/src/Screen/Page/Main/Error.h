#pragma once

#include "Screen/Page/Main/Info.h"

namespace Screen {

// Упрощенный фасад показа обычной ошибки через Info.
class Error {
public:
    // Показать сообщение об ошибке.
    static void show(const char* message) {
        Info::showInfo("Error", message);
    }
};

}  // namespace Screen
