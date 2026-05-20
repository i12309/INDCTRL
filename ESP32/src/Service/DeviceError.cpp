#include "DeviceError.h"

// Вернуть singleton хранилища ошибки.
DeviceError& DeviceError::instance() {
    static DeviceError errors;
    return errors;
}

// Записать текст ошибки.
void DeviceError::set(String message) {
    message_ = message;
}

// Очистить текст ошибки.
void DeviceError::clear() {
    message_ = "";
}

// Проверить наличие текста ошибки.
bool DeviceError::hasError() const {
    return message_.length() > 0;
}

// Вернуть текущий текст ошибки.
const String& DeviceError::message() const {
    return message_;
}
