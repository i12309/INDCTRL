#include "Log.h"

void Log::init(unsigned long baud) {
    Serial.begin(baud);
}

void Log::info(const char* format, ...) {
    va_list args;
    va_start(args, format);
    write("INFO", format, args);
    va_end(args);
}

void Log::warn(const char* format, ...) {
    va_list args;
    va_start(args, format);
    write("WARN", format, args);
    va_end(args);
}

void Log::error(const char* format, ...) {
    va_list args;
    va_start(args, format);
    write("ERROR", format, args);
    va_end(args);
}

void Log::write(const char* level, const char* format, va_list args) {
    char buffer[256];
    vsnprintf(buffer, sizeof(buffer), format, args);
    Serial.printf("[%s] %s\n", level, buffer);
}
