#include "Main.h"

#include "Screen/Page/Main/Process.h"

namespace Screen {

Main::Main() : Page(SCREEN_ID_PROCESS) {}

// Вернуть singleton страницы.
Main& Main::instance() {
    static Main page;
    return page;
}

// Main оставлен для совместимости и сразу открывает настоящий экран Process.
void Main::onShow() {
    Process::instance().show();
}

}  // namespace Screen
