#pragma once

#include <cstddef>

#include "Screen/Page/Page.h"

namespace Screen {

class Details : public Page {
public:
    static Details& instance();

protected:
    void onPrepare() override;
    void onShow() override;

private:
    Details();
    void loadDetails();
    void render();

    static void popBack(lv_event_t* e);
    static void popNext(lv_event_t* e);

    size_t offset_ = 0;
};

}  // namespace Screen
