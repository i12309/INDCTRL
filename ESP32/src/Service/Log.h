#pragma once

#include <Arduino.h>

class Log {
public:
    static void init(unsigned long baud = 115200);
    static void info(const char* format, ...);
    static void warn(const char* format, ...);
    static void error(const char* format, ...);

private:
    static void write(const char* level, const char* format, va_list args);
};
