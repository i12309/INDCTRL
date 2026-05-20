#pragma once

#include <Arduino.h>

#include "Screen/Page/Page.h"

namespace Screen {

// Универсальная информационная страница с сообщением и кнопкой OK.
class Info : public Page {
public:
    // Вернуть singleton страницы Info.
    static Info& instance();
    // Показать информационное окно с заголовком и сообщением.
    static void showInfo(const char* title, const char* message);
    // Показать информационное окно с дополнительной строкой detail.
    static void showInfo(const char* title, const char* message, const char* detail);
    // Показать ошибку, после OK выполнить ESP.restart().
    static void showRestart(const char* title, const char* message);
    // Показать ошибку с detail, после OK выполнить ESP.restart().
    static void showRestart(const char* title, const char* message, const char* detail);

protected:
    // Привязать OK и Back к одному обработчику закрытия.
    void onPrepare() override;
    // Перерисовать тексты при показе.
    void onShow() override;

private:
    // Создать страницу и связать ее с EEZ SCREEN_ID_INFO.
    Info();
    // Записать title/message/detail в LVGL-объекты.
    void render();

    // Закрыть Info или перезапустить устройство, если включен restartOnOk_.
    static void popOk(lv_event_t* e);

    // Заголовок окна.
    String title_ = "Info";
    // Основной текст сообщения.
    String message_;
    // Дополнительная строка с деталями.
    String detail_;
    // true, если OK должен перезагрузить ESP32.
    bool restartOnOk_ = false;
};

}  // namespace Screen
