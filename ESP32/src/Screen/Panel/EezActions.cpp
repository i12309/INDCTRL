#include <lvgl/lvgl.h>

// Заглушка EEZ action для текстовой клавиатуры; реальная логика кнопок живет в Page-слое.
extern "C" void action_keyboard_text(lv_event_t* e) {
    (void)e;
}

// Заглушка EEZ action для цифровой клавиатуры; обработчики назначаются вручную в Number.
extern "C" void action_keyboard_number(lv_event_t* e) {
    (void)e;
}
