#include "Process.h"

#include <Arduino.h>

#include "Data.h"
#include "Screen/Page/Main/Details.h"
#include "Screen/Page/Main/Info.h"
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
    ApiResult result = DeviceApi::logout(Data::runtime.sessionId);
    if (!result.success) {
        Info::showInfo("Ошибка завершения", result.error.c_str());
        return;
    }

    Data::runtime.clearSession();
    ESP.restart();
}

}  // namespace Screen
