#include "Details.h"

#include "Data.h"
#include "Screen/Page/Main/Info.h"
#include "Screen/Panel/LvglHelpers.h"
#include "Service/DeviceApi.h"

#include <ui/screens.h>

namespace Screen {

namespace {
// Количество строк деталей, помещающихся на экране.
constexpr size_t PAGE_SIZE = 6;

// Вернуть label номера детали по индексу строки.
lv_obj_t* paramAt(size_t index) {
    lv_obj_t* items[] = {
        objects.details_param1,
        objects.details_param2,
        objects.details_param3,
        objects.details_param4,
        objects.details_param5,
        objects.details_param6,
    };
    return index < PAGE_SIZE ? items[index] : nullptr;
}

// Вернуть label состояния детали по индексу строки.
lv_obj_t* valueAt(size_t index) {
    lv_obj_t* items[] = {
        objects.details_value1,
        objects.details_value2,
        objects.details_value3,
        objects.details_value4,
        objects.details_value5,
        objects.details_value6,
    };
    return index < PAGE_SIZE ? items[index] : nullptr;
}

// Вернуть label времени детали по индексу строки.
lv_obj_t* timeAt(size_t index) {
    lv_obj_t* items[] = {
        objects.details_time1,
        objects.details_time2,
        objects.details_time3,
        objects.details_time4,
        objects.details_time5,
        objects.details_time6,
    };
    return index < PAGE_SIZE ? items[index] : nullptr;
}
}  // namespace

Details::Details() : Page(SCREEN_ID_DETAILS) {}

// Вернуть singleton страницы.
Details& Details::instance() {
    static Details page;
    return page;
}

// Подключить кнопки листания.
void Details::onPrepare() {
    Ui::onPop(objects.details_back, Details::popBack);
    Ui::onPop(objects.details_next, Details::popNext);
}

// При каждом входе начинаем с первой страницы и обновляем список с сервера.
void Details::onShow() {
    offset_ = 0;
    loadDetails();
    render();
}

// Загрузить детали активной смены.
void Details::loadDetails() {
    // Без sessionID сервер не сможет понять, какую смену показывать.
    if (Data::runtime.sessionId.length() == 0) return;

    ApiResult result = DeviceApi::loadDetails(Data::runtime.sessionId, Data::runtime.details);
    if (!result.success) {
        // Таймаут оставляет пользователя на текущем экране без всплывающей ошибки.
        if (result.timedOut) return;

        Info::showInfo("Ошибка деталей", result.error.c_str());
    }
}

// Отрисовать текущую страницу деталей.
void Details::render() {
    const size_t total = Data::runtime.details.size();
    Ui::setHidden(objects.details_next, offset_ + PAGE_SIZE >= total);

    for (size_t i = 0; i < PAGE_SIZE; ++i) {
        const size_t detailIndex = offset_ + i;
        const bool visible = detailIndex < total;

        Ui::setHidden(paramAt(i), !visible);
        Ui::setHidden(valueAt(i), !visible);
        Ui::setHidden(timeAt(i), !visible);

        // Невидимые строки не заполняем, чтобы не мигали старые значения.
        if (!visible) continue;

        const DetailData& detail = Data::runtime.details[detailIndex];
        Ui::setText(paramAt(i), String(detail.number));
        Ui::setText(valueAt(i), detail.state);
        Ui::setText(timeAt(i), detail.time);
    }
}

// Листнуть назад или вернуться на Process с первой страницы.
void Details::popBack(lv_event_t* e) {
    (void)e;
    Details& page = instance();
    if (page.offset_ >= PAGE_SIZE) {
        page.offset_ -= PAGE_SIZE;
        page.render();
        return;
    }

    page.back();
}

// Листнуть вперед, если есть следующая страница деталей.
void Details::popNext(lv_event_t* e) {
    (void)e;
    Details& page = instance();
    if (page.offset_ + PAGE_SIZE < Data::runtime.details.size()) {
        page.offset_ += PAGE_SIZE;
        page.render();
    }
}

}  // namespace Screen
