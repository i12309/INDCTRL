#pragma once

#include <Arduino.h>
#include <ArduinoJson.h>

// Низкоуровневый HTTP JSON-клиент для запросов ESP32 к WEB API.
class ApiClient {
public:
    // Последняя транспортная ошибка клиента.
    enum class Error {
        // Ошибки нет.
        None,
        // Передан пустой или некорректный путь API.
        InvalidPath,
        // HTTPClient не смог начать запрос.
        BeginFailed,
        // Запрос не выполнился на транспортном уровне.
        RequestFailed,
        // Сервер не ответил за заданный таймаут.
        Timeout,
        // Ответ сервера не удалось разобрать как JSON.
        JsonParse
    };

    // Создать клиент с явным baseUrl или адресом из Config.
    explicit ApiClient(String baseUrl = "");

    // Изменить базовый адрес API.
    void setBaseUrl(const String& baseUrl);
    // Вернуть текущий базовый адрес API.
    const String& baseUrl() const;
    // Вернуть последнюю транспортную ошибку.
    Error lastError() const;
    // Вернуть последний HTTP-статус.
    int lastStatus() const;

    // Отправить POST JSON и разобрать JSON-ответ; при waitTitle показывает экран ожидания.
    bool postJson(const char* path, JsonDocument& request, JsonDocument& response, const char* waitTitle = nullptr);

private:
    // Базовый URL сервера без конечного path.
    String baseUrl_;
    // Последняя ошибка, нужна верхнему уровню для понятного сообщения.
    Error lastError_ = Error::None;
    // HTTP-статус последнего ответа.
    int lastStatus_ = 0;
};
