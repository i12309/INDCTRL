#pragma once

#include <Arduino.h>

#include "Screen/Page/Page.h"

namespace Screen {

// Страница цифрового PIN-ввода для входа и подтверждения закрытия смены.
class Number : public Page {
public:
    // Вернуть singleton страницы Number.
    static Number& instance();
    // Открыть клавиатуру в режиме входа в смену.
    void showLogin();
    // Открыть клавиатуру в режиме закрытия смены.
    void showCloseShift();

protected:
    // Привязать все цифровые кнопки и управляющие кнопки.
    void onPrepare() override;
    // Очистить введенный PIN при каждом показе.
    void onShow() override;

private:
    // Режим определяет, что делает OK и куда ведет Отмена.
    enum class Mode {
        // Ввод PIN для login.
        Login,
        // Ввод PIN для подтверждения logout.
        CloseShift,
    };

    // Создать страницу и связать ее с EEZ SCREEN_ID_NUMBER.
    Number();

    // Добавить цифру к текущему PIN.
    static void popDigit(lv_event_t* e);
    // Удалить последнюю цифру PIN.
    static void popBackspace(lv_event_t* e);
    // Отменить ввод и вернуться на нужный экран текущего режима.
    static void popCancel(lv_event_t* e);
    // Подтвердить ввод PIN.
    static void popOk(lv_event_t* e);
    // Разобрать введенный PIN и направить в login или logout.
    static void submit();
    // Выполнить login с выбранным работником и введенным PIN.
    void submitLogin(const String& password);
    // Выполнить logout текущей сессии с введенным PIN.
    void submitCloseShift(const String& password);

    // Текущий режим клавиатуры.
    Mode mode_ = Mode::Login;
};

}  // namespace Screen
