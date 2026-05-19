#pragma once

#include <Arduino.h>

class DeviceError {
public:
    static DeviceError& instance();

    void set(String message);
    void clear();
    bool hasError() const;
    const String& message() const;

private:
    DeviceError() = default;
    String message_;
};
