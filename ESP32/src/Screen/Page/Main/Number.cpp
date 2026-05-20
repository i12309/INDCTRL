#include "Number.h"

#include "Data.h"
#include "Screen/Page/Main/Info.h"
#include "Screen/Page/Main/List.h"
#include "Screen/Page/Main/Load.h"
#include "Screen/Page/Main/Process.h"
#include "Screen/Panel/LvglHelpers.h"
#include "Service/DeviceApi.h"
#include "State/State.h"
#include "State/System/Idle.h"
#include "State/System/Process.h"

#include <ui/screens.h>

namespace Screen {

Number::Number() : Page(SCREEN_ID_NUMBER) {}

// Вернуть singleton страницы.
Number& Number::instance() {
    static Number page;
    return page;
}

// Открыть клавиатуру для входа работника.
void Number::showLogin() {
    mode_ = Mode::Login;
    show();
}

// Открыть клавиатуру после выбора работника администратором.
void Number::showWorkerLogin() {
    mode_ = Mode::WorkerLogin;
    show();
}

// Открыть клавиатуру для подтверждения закрытия смены.
void Number::showCloseShift() {
    mode_ = Mode::CloseShift;
    show();
}

// Привязать обработчики всех кнопок PIN-клавиатуры.
void Number::onPrepare() {
    Ui::onPop(objects.kbd_0, Number::popDigit, (void*)"0");
    Ui::onPop(objects.kbd_1, Number::popDigit, (void*)"1");
    Ui::onPop(objects.kbd_2, Number::popDigit, (void*)"2");
    Ui::onPop(objects.kbd_3, Number::popDigit, (void*)"3");
    Ui::onPop(objects.kbd_4, Number::popDigit, (void*)"4");
    Ui::onPop(objects.kbd_5, Number::popDigit, (void*)"5");
    Ui::onPop(objects.kbd_6, Number::popDigit, (void*)"6");
    Ui::onPop(objects.kbd_7, Number::popDigit, (void*)"7");
    Ui::onPop(objects.kbd_8, Number::popDigit, (void*)"8");
    Ui::onPop(objects.kbd_9, Number::popDigit, (void*)"9");
    Ui::onPop(objects.kbd_backspace, Number::popBackspace);
    Ui::onPop(objects.kbd_cancel, Number::popCancel);
    Ui::onPop(objects.kbd_ok, Number::popOk);
}

// Очистить поле PIN при каждом показе.
void Number::onShow() {
    Ui::setText(objects.kbd_text, "");
}

// Добавить нажатую цифру в поле PIN.
void Number::popDigit(lv_event_t* e) {
    const char* digit = static_cast<const char*>(lv_event_get_user_data(e));
    // userData обязан содержать строку цифры; без нее кнопку игнорируем.
    if (digit == nullptr) return;

    String value = Ui::getText(objects.kbd_text);
    // Ограничение защищает от бесконечного роста строки при случайном удержании/многоклике.
    if (value.length() >= 10) return;
    value += digit;
    Ui::setText(objects.kbd_text, value);
}

// Удалить последнюю цифру PIN.
void Number::popBackspace(lv_event_t* e) {
    (void)e;
    String value = Ui::getText(objects.kbd_text);
    if (value.length() == 0) return;
    value.remove(value.length() - 1);
    Ui::setText(objects.kbd_text, value);
}

// Отменить ввод и вернуться на экран, соответствующий режиму клавиатуры.
void Number::popCancel(lv_event_t* e) {
    (void)e;
    // При закрытии смены возвращаемся на Process явно, потому что Info может сбросить previousPage.
    if (instance().mode_ == Mode::CloseShift) {
        Process::instance().show();
        return;
    }
    if (instance().mode_ == Mode::WorkerLogin) {
        List::instance().show();
        return;
    }
    Data::runtime.clearSession();
    Screen::Load::instance().show();
}

// Подтвердить введенный PIN.
void Number::popOk(lv_event_t* e) {
    (void)e;
    submit();
}

// Выбрать действие по текущему режиму клавиатуры.
void Number::submit() {
    String pin = Ui::getText(objects.kbd_text);
    pin.trim();
    // Пустой PIN не отправляем на сервер, чтобы не показывать лишнюю ошибку API.
    if (pin.length() == 0) return;

    Number& page = instance();
    // Один экран используется для двух сценариев: login и подтверждение logout.
    if (page.mode_ == Mode::CloseShift) {
        page.submitCloseShift(pin);
        return;
    }

    page.submitLogin(pin);
}

// Отправить login и сохранить данные сессии из ответа сервера.
void Number::submitLogin(const String& pin) {
    LoginResult result = DeviceApi::login(pin, Data::runtime.deviceMac);
    if (!result.success) {
        // При таймауте WaitGuard уже вернул UI, оставляем экран без дополнительной ошибки.
        if (result.timedOut) return;

        Ui::setText(objects.kbd_text, "");
        // Занятый станок требует перезапуска, чтобы пользователь видел актуальное состояние после OK.
        if (result.error.indexOf("занят") >= 0) {
            Info::showRestart("Ошибка входа", result.error.c_str());
            return;
        }

        Info::showInfo("Ошибка входа", result.error.c_str());
        return;
    }

    if (result.isAdmin) {
        Data::runtime.machineId = result.machineId;
        Data::runtime.machineName = "";
        Data::runtime.workers.clear();
        List::instance().show();
        return;
    }

    Data::runtime.sessionId = result.sessionId;
    Data::runtime.userId = result.userId;
    Data::runtime.machineId = result.machineId;
    Data::runtime.workId = result.workId;
    Data::runtime.workerName = result.fullName;
    State::set(new ::WorkProcess());
}

// Отправить logout текущей сессии и перезапустить устройство после успешного закрытия.
void Number::submitCloseShift(const String& pin) {
    ApiResult logout = DeviceApi::logout(Data::runtime.sessionId, pin);
    if (!logout.success) {
        // Таймаут не очищает сессию, чтобы пользователь мог повторить закрытие.
        if (logout.timedOut) return;

        Ui::setText(objects.kbd_text, "");
        Info::showInfo("Ошибка завершения", logout.error.c_str());
        return;
    }

    Data::runtime.clearSession();
    State::set(new ::Idle());
}

}  // namespace Screen
