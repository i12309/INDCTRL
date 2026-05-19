#pragma once

#include "Service/ApiClient.h"

class Service {
public:
    static void init();
    static void process();
    static ApiClient& api();
};
