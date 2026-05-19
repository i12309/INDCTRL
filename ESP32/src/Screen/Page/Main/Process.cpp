#include "Process.h"

#include <Arduino.h>

#include "Data.h"
#include "Screen/Page/Main/Details.h"
#include "Screen/Page/Main/Info.h"
#include "Screen/Page/Main/Number.h"
#include "Screen/Panel/LvglHelpers.h"
#include "Service/DeviceApi.h"

#include <ui/screens.h>

namespace Screen {

Process::Process() : Page(SCREEN_ID_PROCESS) {}

Process& Process::instance() {
    static Process page;
    return page;
}

void Process::onPrepare() {
    Ui::onPop(objects.process_details, Process::popDetails);
    Ui::onPop(objects.process_close, Process::popClose);
}

void Process::onShow() {
    render();
}

void Process::render() {
    Ui::setText(objects.process_title, String("Смена ") + Data::runtime.workId);
    Ui::setText(objects.process_fio, Data::runtime.workerName);

    int maxNumber = 0;
    String lastState = "-";
    for (const DetailData& detail : Data::runtime.details) {
        if (detail.number > maxNumber) {
            maxNumber = detail.number;
            lastState = detail.state;
        }
    }

    Ui::setText(objects.process_count, String(maxNumber));
    Ui::setText(objects.process_status, lastState);
}

void Process::popDetails(lv_event_t* e) {
    (void)e;
    Details::instance().show();
}

void Process::popClose(lv_event_t* e) {
    (void)e;
    Number::instance().showCloseShift();
}

}  // namespace Screen
