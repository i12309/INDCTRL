#pragma once

#include <Arduino.h>
#include <vector>

// Краткая запись о работнике, которую ESP32 получает из WEB API для экрана выбора.
struct WorkerData {
    // Идентификатор пользователя в Django, используется при login.
    int userId = 0;
    // Отображаемое ФИО работника на экране списка.
    String fullName;
};

// Краткая запись о детали текущей смены для экрана Details и счетчиков Process.
struct DetailData {
    // Номер детали внутри смены.
    int number = 0;
    // Текстовое состояние детали, сейчас приходит как процент качества.
    String state;
    // Локальное время события детали строкой для отображения.
    String time;
};

// Общие runtime-данные устройства, живущие до перезагрузки ESP32.
struct RuntimeData {
    // MAC-адрес ESP32, по нему сервер определяет устройство и станок.
    String deviceMac;
    // Текущий sessionID активной смены; пустая строка означает отсутствие смены.
    String sessionId;
    // Текущий пользователь, выбранный или вошедший в смену.
    int userId = 0;
    // Станок, связанный с устройством на сервере.
    int machineId = 0;
    // ID активной рабочей смены на сервере.
    int workId = 0;
    // ФИО текущего работника для экрана Process.
    String workerName;
    // Название станка, полученное из API работников.
    String machineName;
    // Список работников, доступных для входа на этом устройстве.
    std::vector<WorkerData> workers;
    // Список деталей текущей смены, полученный с сервера.
    std::vector<DetailData> details;

    // Очистить все данные, привязанные к активной смене, после logout или перезапуска сценария.
    void clearSession() {
        sessionId = "";
        userId = 0;
        machineId = 0;
        workId = 0;
        workerName = "";
        details.clear();
    }
};

// Глобальное хранилище runtime-данных прошивки.
class Data {
public:
    // Единственный экземпляр данных, к которому обращаются экраны и сервисы.
    static RuntimeData runtime;
};
