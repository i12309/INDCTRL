#pragma once

#include <Arduino.h>

// Глобальное хранилище последней ошибки устройства.
class DeviceError {
public:
    // Вернуть singleton ошибки.
    static DeviceError& instance();

    // Установить текст активной ошибки.
    void set(String message);
    // Очистить активную ошибку.
    void clear();
    // Проверить, есть ли сейчас ошибка.
    bool hasError() const;
    // Вернуть текст текущей ошибки.
    const String& message() const;

private:
    // Запрещаем внешнее создание, чтобы ошибка была единой.
    DeviceError() = default;
    // Текст активной ошибки.
    String message_;
};
