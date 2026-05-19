#include "Main.h"

#include "Screen/Page/Main/Process.h"

namespace Screen {

Main::Main() : Page(SCREEN_ID_PROCESS) {}

Main& Main::instance() {
    static Main page;
    return page;
}

void Main::onShow() {
    Process::instance().show();
}

}  // namespace Screen
