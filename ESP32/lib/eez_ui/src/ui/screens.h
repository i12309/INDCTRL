#ifndef EEZ_LVGL_UI_SCREENS_H
#define EEZ_LVGL_UI_SCREENS_H

#include <lvgl/lvgl.h>

#ifdef __cplusplus
extern "C" {
#endif

// Screens

enum ScreensEnum {
    _SCREEN_ID_FIRST = 1,
    SCREEN_ID_LOAD0 = 1,
    SCREEN_ID_LOAD = 2,
    SCREEN_ID_LIST = 3,
    SCREEN_ID_PROCESS = 4,
    SCREEN_ID_DETAILS = 5,
    SCREEN_ID_INFO = 6,
    SCREEN_ID_WAIT = 7,
    SCREEN_ID_NUMBER = 8,
    _SCREEN_ID_LAST = 8
};

typedef struct _objects_t {
    lv_obj_t *load0;
    lv_obj_t *load;
    lv_obj_t *list;
    lv_obj_t *process;
    lv_obj_t *details;
    lv_obj_t *info;
    lv_obj_t *wait;
    lv_obj_t *number;
    lv_obj_t *obj0;
    lv_obj_t *obj1;
    lv_obj_t *obj2;
    lv_obj_t *obj3;
    lv_obj_t *obj4;
    lv_obj_t *obj5;
    lv_obj_t *obj6;
    lv_obj_t *obj7;
    lv_obj_t *obj8;
    lv_obj_t *obj9;
    lv_obj_t *obj10;
    lv_obj_t *obj11;
    lv_obj_t *load_ma_caddress;
    lv_obj_t *load_version;
    lv_obj_t *obj12;
    lv_obj_t *obj13;
    lv_obj_t *list_back;
    lv_obj_t *obj14;
    lv_obj_t *list_next;
    lv_obj_t *list_item_1;
    lv_obj_t *list_item_2;
    lv_obj_t *list_item_3;
    lv_obj_t *list_item_4;
    lv_obj_t *list_item_5;
    lv_obj_t *list_item_6;
    lv_obj_t *obj15;
    lv_obj_t *obj16;
    lv_obj_t *process_title;
    lv_obj_t *obj17;
    lv_obj_t *obj18;
    lv_obj_t *process_fio;
    lv_obj_t *obj19;
    lv_obj_t *process_count;
    lv_obj_t *obj20;
    lv_obj_t *process_status;
    lv_obj_t *obj21;
    lv_obj_t *process_details;
    lv_obj_t *process_close;
    lv_obj_t *obj22;
    lv_obj_t *obj23;
    lv_obj_t *details_back;
    lv_obj_t *stats_title;
    lv_obj_t *obj24;
    lv_obj_t *details_next;
    lv_obj_t *obj25;
    lv_obj_t *obj26;
    lv_obj_t *obj27;
    lv_obj_t *details_param1;
    lv_obj_t *details_value1;
    lv_obj_t *details_time1;
    lv_obj_t *details_param2;
    lv_obj_t *details_value2;
    lv_obj_t *details_time2;
    lv_obj_t *details_param3;
    lv_obj_t *details_value3;
    lv_obj_t *details_time3;
    lv_obj_t *details_param4;
    lv_obj_t *details_value4;
    lv_obj_t *details_time4;
    lv_obj_t *details_param5;
    lv_obj_t *details_value5;
    lv_obj_t *details_time5;
    lv_obj_t *details_param6;
    lv_obj_t *details_value6;
    lv_obj_t *details_time6;
    lv_obj_t *obj28;
    lv_obj_t *obj29;
    lv_obj_t *info_back;
    lv_obj_t *obj30;
    lv_obj_t *info_next;
    lv_obj_t *info_field1;
    lv_obj_t *info_field2;
    lv_obj_t *info_field3;
    lv_obj_t *info_ok;
    lv_obj_t *obj31;
    lv_obj_t *obj32;
    lv_obj_t *wait_title;
    lv_obj_t *obj33;
    lv_obj_t *wait_field1;
    lv_obj_t *wait_field2;
    lv_obj_t *wait_field3;
    lv_obj_t *obj34;
    lv_obj_t *kbd_text;
    lv_obj_t *kbd_1;
    lv_obj_t *kbd_2;
    lv_obj_t *kbd_3;
    lv_obj_t *kbd_ok;
    lv_obj_t *kbd_4;
    lv_obj_t *kbd_5;
    lv_obj_t *kbd_6;
    lv_obj_t *kbd_backspace;
    lv_obj_t *kbd_7;
    lv_obj_t *kbd_8;
    lv_obj_t *kbd_9;
    lv_obj_t *kbd_cancel;
    lv_obj_t *obj35;
    lv_obj_t *kbd_0;
    lv_obj_t *obj36;
    lv_obj_t *obj37;
} objects_t;

extern objects_t objects;

void create_screen_load0();
void tick_screen_load0();

void create_screen_load();
void tick_screen_load();

void create_screen_list();
void tick_screen_list();

void create_screen_process();
void tick_screen_process();

void create_screen_details();
void tick_screen_details();

void create_screen_info();
void tick_screen_info();

void create_screen_wait();
void tick_screen_wait();

void create_screen_number();
void tick_screen_number();

void create_user_widget_123(lv_obj_t *parent_obj, int startWidgetIndex);
void tick_user_widget_123(int startWidgetIndex);

void tick_screen_by_id(enum ScreensEnum screenId);
void tick_screen(int screen_index);

void create_screens();

#ifdef __cplusplus
}
#endif

#endif /*EEZ_LVGL_UI_SCREENS_H*/