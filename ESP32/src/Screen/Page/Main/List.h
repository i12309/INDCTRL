#pragma once

#include <cstddef>

#include "Screen/Page/Page.h"

namespace Screen {

class List : public Page {
public:
    static List& instance();

protected:
    void onPrepare() override;
    void onShow() override;

private:
    List();
    bool loadWorkers();
    void render();

    static void popBack(lv_event_t* e);
    static void popNext(lv_event_t* e);
    static void popItem(lv_event_t* e);

    size_t offset_ = 0;
};

}  // namespace Screen
