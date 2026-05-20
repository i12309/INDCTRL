#pragma once

#include "Screen/Page/Page.h"

namespace Screen {

// Страница загрузки с логотипом, MAC, версией и ожиданием касания.
class Load : public Page {
public:
    // Вернуть singleton страницы Load.
    static Load& instance();
    // Задать служебный текст загрузки для будущего отображения.
    void setText(const char* text);
    // Проверить, попросил ли пользователь продолжить касанием Load.
    bool continueRequested() const;

protected:
    // Привязать обработчики касания к Load и его видимым элементам.
    void onPrepare() override;
    // Сбросить флаг продолжения и вывести MAC/версию.
    void onShow() override;

private:
    // Создать страницу и связать ее с EEZ SCREEN_ID_LOAD.
    Load();
    // Отметить, что пользователь коснулся экрана загрузки.
    static void popContinue(lv_event_t* e);
    // Сделать объект кликабельным и привязать к нему popContinue().
    void registerContinueTarget(lv_obj_t* obj);

    // Текст загрузки; сейчас хранится для совместимости со старым API.
    const char* text_ = "Loading...";
    // Флаг пользовательского касания для перехода Boot -> Idle.
    bool continueRequested_ = false;
};

}  // namespace Screen
