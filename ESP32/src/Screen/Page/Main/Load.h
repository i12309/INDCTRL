#pragma once

#include "Screen/Page/Page.h"

namespace Screen {

class Load : public Page {
public:
    static Load& instance();
    void setText(const char* text);

protected:
    void onShow() override;

private:
    Load();
    const char* text_ = "Loading...";
};

}  // namespace Screen
