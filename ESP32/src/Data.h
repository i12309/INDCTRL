#pragma once

#include <Arduino.h>
#include <vector>

struct WorkerData {
    int userId = 0;
    String fullName;
};

struct DetailData {
    int number = 0;
    String state;
    String time;
};

struct RuntimeData {
    String deviceMac;
    String sessionId;
    int userId = 0;
    int machineId = 0;
    int workId = 0;
    String workerName;
    String machineName;
    std::vector<WorkerData> workers;
    std::vector<DetailData> details;

    void clearSession() {
        sessionId = "";
        userId = 0;
        machineId = 0;
        workId = 0;
        workerName = "";
        details.clear();
    }
};

class Data {
public:
    static RuntimeData runtime;
};
