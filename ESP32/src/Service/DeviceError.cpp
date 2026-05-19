#include "DeviceError.h"

DeviceError& DeviceError::instance() {
    static DeviceError errors;
    return errors;
}

void DeviceError::set(String message) {
    message_ = message;
}

void DeviceError::clear() {
    message_ = "";
}

bool DeviceError::hasError() const {
    return message_.length() > 0;
}

const String& DeviceError::message() const {
    return message_;
}
