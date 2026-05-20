#pragma once

#include <Arduino.h>

// Обертка над Serial для единообразных логов прошивки.
class Log {
public:
    // Инициализировать Serial с заданной скоростью.
    static void init(unsigned long baud = 115200);
    // Записать информационное сообщение.
    static void info(const char* format, ...);
    // Записать предупреждение.
    static void warn(const char* format, ...);
    // Записать ошибку.
    static void error(const char* format, ...);

private:
    // Общая реализация форматированной записи с уровнем.
    static void write(const char* level, const char* format, va_list args);
};
