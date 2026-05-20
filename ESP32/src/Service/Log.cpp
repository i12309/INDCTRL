#include "Log.h"

// Запустить Serial для диагностических сообщений.
void Log::init(unsigned long baud) {
    Serial.begin(baud);
}

// Записать INFO-сообщение.
void Log::info(const char* format, ...) {
    va_list args;
    va_start(args, format);
    write("INFO", format, args);
    va_end(args);
}

// Записать WARN-сообщение.
void Log::warn(const char* format, ...) {
    va_list args;
    va_start(args, format);
    write("WARN", format, args);
    va_end(args);
}

// Записать ERROR-сообщение.
void Log::error(const char* format, ...) {
    va_list args;
    va_start(args, format);
    write("ERROR", format, args);
    va_end(args);
}

// Отформатировать сообщение в буфер и вывести в Serial.
void Log::write(const char* level, const char* format, va_list args) {
    char buffer[256];
    vsnprintf(buffer, sizeof(buffer), format, args);
    Serial.printf("[%s] %s\n", level, buffer);
}
