#pragma once

#include <Arduino.h>
#include <ArduinoJson.h>
#include <vector>

#include "Data.h"

struct ApiResult {
    bool success = false;
    bool timedOut = false;
    String error;
};

struct LoginResult {
    bool success = false;
    bool timedOut = false;
    String error;
    String sessionId;
    int userId = 0;
    int machineId = 0;
    int workId = 0;
};

class DeviceApi {
public:
    static ApiResult loadWorkers(const String& macAddress, int& machineId, String& machineName, std::vector<WorkerData>& workers);
    static LoginResult login(int userId, const String& password, const String& macAddress);
    static ApiResult logout(const String& sessionId);
    static ApiResult heartbeat(const String& sessionId);
    static ApiResult loadDetails(const String& sessionId, std::vector<DetailData>& details);

private:
    static ApiResult resultFromResponse(bool httpOk, JsonDocument& response);
};
