#pragma once

// Инициализация и обслуживание экрана, тача и LVGL/EEZ UI.
class Panel {
public:
    // Запустить дисплей, LVGL, EEZ и подготовить первый экран.
    static void init();
    // Обработать один цикл LVGL и EEZ.
    static void process();
    // Проверить, была ли панель успешно инициализирована.
    static bool isInitialized();
};
