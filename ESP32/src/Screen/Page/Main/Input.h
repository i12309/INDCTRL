#pragma once

#include "Screen/Page/Main/Info.h"

namespace Screen {

// Заглушка будущей страницы ввода, пока весь ввод идет через Number.
class Input {
public:
    // Показать placeholder, чтобы вызовы Input не ломали UI.
    static void showPlaceholder() {
        Info::showInfo("Input", "Input page placeholder");
    }
};

}  // namespace Screen
