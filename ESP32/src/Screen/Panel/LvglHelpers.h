#pragma once

#include <Arduino.h>
#include <lvgl/lvgl.h>

namespace Ui {

// Найти первый label внутри объекта; нужен для кнопок EEZ, где текст лежит дочерним label.
inline lv_obj_t* firstLabel(lv_obj_t* obj) {
    if (obj == nullptr) return nullptr;

    const uint32_t childCount = lv_obj_get_child_count(obj);
    for (uint32_t i = 0; i < childCount; ++i) {
        lv_obj_t* child = lv_obj_get_child(obj, static_cast<int32_t>(i));
        if (child != nullptr && lv_obj_check_type(child, &lv_label_class)) return child;
    }

    return nullptr;
}

// Привязать обработчик отпускания кнопки к LVGL-объекту.
inline void onPop(lv_obj_t* obj, lv_event_cb_t cb, void* userData = nullptr) {
    if (obj == nullptr || cb == nullptr) return;
    lv_obj_add_event_cb(obj, cb, LV_EVENT_RELEASED, userData);
}

// Установить текст в label, textarea или внутренний label контейнера/кнопки.
inline void setText(lv_obj_t* obj, const String& text) {
    if (obj == nullptr) return;

    const char* value = text.c_str();
    // Label и textarea обновляются разными API LVGL, поэтому тип проверяется явно.
    if (lv_obj_check_type(obj, &lv_label_class)) {
        lv_label_set_text(obj, value);
        return;
    }

    if (lv_obj_check_type(obj, &lv_textarea_class)) {
        lv_textarea_set_text(obj, value);
        return;
    }

    lv_obj_t* label = firstLabel(obj);
    if (label != nullptr) lv_label_set_text(label, value);
}

// Перегрузка для C-строк, чтобы вызовы из экранов были короче.
inline void setText(lv_obj_t* obj, const char* text) {
    setText(obj, String(text == nullptr ? "" : text));
}

// Прочитать текст из label, textarea или внутреннего label.
inline String getText(lv_obj_t* obj) {
    if (obj == nullptr) return "";

    if (lv_obj_check_type(obj, &lv_label_class)) {
        return String(lv_label_get_text(obj));
    }

    if (lv_obj_check_type(obj, &lv_textarea_class)) {
        return String(lv_textarea_get_text(obj));
    }

    lv_obj_t* label = firstLabel(obj);
    if (label != nullptr) return String(lv_label_get_text(label));

    return "";
}

// Скрыть или показать объект без пересоздания экрана.
inline void setHidden(lv_obj_t* obj, bool hidden) {
    if (obj == nullptr) return;
    if (hidden) {
        lv_obj_add_flag(obj, LV_OBJ_FLAG_HIDDEN);
    } else {
        lv_obj_remove_flag(obj, LV_OBJ_FLAG_HIDDEN);
    }
}

}  // namespace Ui
