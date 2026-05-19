#pragma once

#include "Screen/Page/Page.h"

namespace Screen {

class Process : public Page {
public:
    static Process& instance();

protected:
    void onPrepare() override;
    void onShow() override;

private:
    Process();
    void render();

    static void popDetails(lv_event_t* e);
    static void popClose(lv_event_t* e);
};

}  // namespace Screen
