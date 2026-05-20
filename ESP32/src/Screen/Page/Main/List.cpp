#include "List.h"

#include <cstdint>

#include "Data.h"
#include "Screen/Page/Main/Info.h"
#include "Screen/Page/Main/Number.h"
#include "Screen/Panel/LvglHelpers.h"
#include "Service/DeviceApi.h"

#include <ui/screens.h>

namespace Screen {

namespace {
// Количество работников, отображаемых на одной странице списка.
constexpr size_t PAGE_SIZE = 6;

// Вернуть объект строки работника по индексу на странице.
lv_obj_t* itemAt(size_t index) {
    lv_obj_t* items[] = {
        objects.list_item_1,
        objects.list_item_2,
        objects.list_item_3,
        objects.list_item_4,
        objects.list_item_5,
        objects.list_item_6,
    };
    return index < PAGE_SIZE ? items[index] : nullptr;
}
}  // namespace

List::List() : Page(SCREEN_ID_LIST) {}

// Вернуть singleton страницы.
List& List::instance() {
    static List page;
    return page;
}

// Подключить листание и обработчики выбора строк.
void List::onPrepare() {
    Ui::onPop(objects.list_back, List::popBack);
    Ui::onPop(objects.list_next, List::popNext);
    // Каждая строка получает индекс 0..5 через userData.
    for (size_t i = 0; i < PAGE_SIZE; ++i) {
        Ui::onPop(itemAt(i), List::popItem, reinterpret_cast<void*>(i));
    }
}

// При показе всегда обновляем список работников с сервера.
void List::onShow() {
    offset_ = 0;
    if (!loadWorkers()) return;
    render();
}

// Загрузить работников, доступных текущему MAC-адресу.
bool List::loadWorkers() {
    ApiResult result = DeviceApi::loadWorkers(
        Data::runtime.deviceMac,
        Data::runtime.machineId,
        Data::runtime.machineName,
        Data::runtime.workers
    );
    if (!result.success) {
        Data::runtime.workers.clear();
        const bool isMacError = result.error.indexOf("MAC") >= 0 || result.error.indexOf("mac") >= 0;
        // Ошибка MAC означает неправильную привязку устройства, поэтому предлагаем перезапуск.
        if (isMacError) {
            Info::showRestart("Ошибка загрузки", result.error.c_str(), Data::runtime.deviceMac.c_str());
            return false;
        }

        Info::showInfo("Ошибка загрузки", result.error.c_str());
        return false;
    }

    // Пустой список означает, что на этом станке сейчас никому нельзя войти.
    if (Data::runtime.workers.empty()) {
        Info::showRestart("Список пуст", "Сотрудники не найдены");
        return false;
    }

    return true;
}

// Отрисовать текущую страницу работников.
void List::render() {
    const size_t total = Data::runtime.workers.size();
    Ui::setHidden(objects.list_back, offset_ == 0);
    Ui::setHidden(objects.list_next, offset_ + PAGE_SIZE >= total);

    for (size_t i = 0; i < PAGE_SIZE; ++i) {
        lv_obj_t* item = itemAt(i);
        const size_t workerIndex = offset_ + i;
        // Невидимые строки скрываем, чтобы по ним нельзя было выбрать старого работника.
        const bool visible = workerIndex < total;
        Ui::setHidden(item, !visible);
        Ui::setText(item, visible ? Data::runtime.workers[workerIndex].fullName : "");
    }
}

// Перейти на предыдущую страницу списка.
void List::popBack(lv_event_t* e) {
    (void)e;
    List& page = instance();
    if (page.offset_ >= PAGE_SIZE) page.offset_ -= PAGE_SIZE;
    page.render();
}

// Перейти на следующую страницу списка, если она есть.
void List::popNext(lv_event_t* e) {
    (void)e;
    List& page = instance();
    if (page.offset_ + PAGE_SIZE < Data::runtime.workers.size()) {
        page.offset_ += PAGE_SIZE;
        page.render();
    }
}

// Выбрать работника и открыть ввод PIN.
void List::popItem(lv_event_t* e) {
    List& page = instance();
    const size_t row = reinterpret_cast<uintptr_t>(lv_event_get_user_data(e));
    const size_t workerIndex = page.offset_ + row;
    // Защита от клика по скрытой или устаревшей строке.
    if (workerIndex >= Data::runtime.workers.size()) return;

    const WorkerData& worker = Data::runtime.workers[workerIndex];
    Data::runtime.userId = worker.userId;
    Data::runtime.workerName = worker.fullName;
    Number::instance().showLogin();
}

}  // namespace Screen
