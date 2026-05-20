#pragma once

#include "Screen/Page/Page.h"

namespace Screen {

class Load : public Page {
public:
    static Load& instance();
    void setText(const char* text);
    bool continueRequested() const;

protected:
    void onPrepare() override;
    void onShow() override;

private:
    Load();
    static void popContinue(lv_event_t* e);
    void registerContinueTarget(lv_obj_t* obj);

    const char* text_ = "Loading...";
    bool continueRequested_ = false;
};

}  // namespace Screen
