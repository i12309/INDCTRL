#pragma once

#include "Service/ApiClient.h"

// Фасад сервисного слоя: сеть, API и фоновые задачи.
class Service {
public:
    // Инициализировать сервисы, которые нужны приложению.
    static void init();
    // Выполнить фоновые сервисные задачи, например heartbeat.
    static void process();
    // Вернуть общий API-клиент.
    static ApiClient& api();
};
