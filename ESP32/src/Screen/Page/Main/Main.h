#pragma once

#include "Screen/Page/Page.h"

namespace Screen {

// Совместимая главная страница, перенаправляющая на Process.
class Main : public Page {
public:
    // Вернуть singleton страницы Main.
    static Main& instance();

protected:
    // При показе открыть Process, где находится основной экран смены.
    void onShow() override;

private:
    // Создать страницу и связать ее с экраном процесса.
    Main();
};

}  // namespace Screen
