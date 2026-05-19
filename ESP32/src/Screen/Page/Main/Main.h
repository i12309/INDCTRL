#pragma once

#include "Screen/Page/Page.h"

namespace Screen {

class Main : public Page {
public:
    static Main& instance();

protected:
    void onShow() override;

private:
    Main();
};

}  // namespace Screen
