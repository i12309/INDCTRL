# План пересоздания Page для EEZ UI

## Контекст

Проект `lib/eez_ui/indCTRL_v1.eez-project` перегенерирован под LVGL 9.4.0, экран 800x480.

Сгенерированные страницы:

- `Load0`
- `Load`
- `List`
- `Number` в проекте EEZ, в C-коде сейчас `SCREEN_ID_KEYBOARD`
- `Process`
- `Details`

Сейчас Page-слой в `src/Screen/Page` рисует экраны вручную через LVGL. Его надо заменить на Page-слой, который работает с EEZ-generated `ui_init()`, `ui_tick()`, `loadScreen()` и объектами из `objects`.

## Главные правила реализации

- Код простой и читаемый, без лишних уровней абстракции.
- Все классы и методы комментируются на русском языке.
- Информационный текст на кнопках пишется во внутренний label `Text`, то есть через helper, который находит label внутри объекта.
- Кнопки без действия остаются обычными элементами отображения: текст обновляем, обработчики не вешаем.
- Сетевые запросы не смешиваем с Page-кодом: для API создаем отдельный класс поверх текущего `ApiClient`.

## Архитектура

### 1. Интеграция EEZ в Panel

Файлы:

- `src/Screen/Panel/Panel.cpp`
- `src/Screen/Panel/LvglHelpers.h`
- `src/Screen/Panel/EezActions.cpp`

Работы:

- Подключить `<ui/ui.h>`.
- В `Panel::init()` вызвать `ui_init()` после `smartdisplay_init()`.
- В `Panel::process()` вызвать `ui_tick()` после `lv_timer_handler()`.
- Добавить `LvglHelpers.h` по образцу `Front32`, но оставить только нужные функции: `setText`, `getText`, `setHidden`, `onPop`, поиск первого label внутри объекта.
- Добавить `EezActions.cpp` с пустыми обработчиками `action_keyboard_text` и `action_keyboard_number`, если действия остаются в EEZ.

### 2. Новый базовый Page

Файлы:

- `src/Screen/Page/Page.h`
- `src/Screen/Page/Page.cpp`

Работы:

- Переделать `Page` с ручного `build(lv_obj_t*)` на хранение `ScreensEnum`.
- `show()` должен вызывать `loadScreen(screenId_)`.
- Добавить `back()` и `previousPage_`, как в `Front32`.
- Добавить `onPrepare()`, который один раз вешает обработчики на EEZ-объекты.
- `process()` оставляет вызов `onTick()` активной страницы.

### 3. Модель данных ESP32 UI

Файлы:

- `src/Data.h`
- `src/Data.cpp`

Работы:

- Хранить MAC устройства.
- Хранить текущую сессию: `sessionID`, `userID`, `machineID`, `workID`, ФИО, номер смены.
- Хранить список работников: `userID`, `login` или фактический идентификатор для login API, `fullName`.
- Хранить список деталей текущей смены: номер, состояние, время.

Вопрос: в текущем WEB API список работников возвращает `userID` и `fullName`, но не возвращает `login`. Нужно решить, добавляем ли `login` в API или на ESP32 используем `userID` как идентификатор для авторизации.

### 4. Класс API для бизнес-запросов

Файлы:

- `src\Service\DeviceApi.h`
- `src\Service\DeviceApi.cpp`
- возможно `src\Service\ApiTypes.h`

Работы:

- Создать простой класс `DeviceApi`, который использует `Service::api()`.
- Методы:
  - `loadWorkers(macAddress, result)`
  - `login(userID/login, password, macAddress, result)`
  - `logout(sessionID)`
  - позже `heartbeat(sessionID)`
  - позже получение деталей, если WEB API будет добавлен
- Разбор JSON держать внутри этого класса.
- Page-код получает уже готовые структуры, а не парсит JSON.

Текущий WEB API:

- `POST /api/device/workers`
- `POST /api/device/login`
- `POST /api/device/detail`
- `POST /api/device/heartbeat`
- `POST /api/device/logout`

Вопрос: для экрана `Details` сейчас нет API получения списка деталей по `sessionID/workID`. Нужно либо добавить endpoint в WEB, либо пока показывать локальные детали, полученные от будущего Wi-Fi устройства.

## Страницы

### 5. Load

Файлы:

- `src/Screen/Page/Main/Load.h`
- `src/Screen/Page/Main/Load.cpp`

EEZ-объекты:

- `objects.load_ma_caddress`
- `objects.load_version`

Поведение:

- При показе вывести MAC адрес ESP32.
- Вывести версию ПО из `Config`.

Нужно добавить в `Config` явную версию, например:

```cpp
inline constexpr const char* APP_VERSION = "0.1.0";
```

Вопрос: версию держим вручную в `config.h` или подключаем генерацию версии по аналогии с `Front32` через pre-build script?

### 6. List

Файлы:

- `src/Screen/Page/Main/List.h`
- `src/Screen/Page/Main/List.cpp`

EEZ-объекты:

- `objects.list_back`
- `objects.list_next`
- `objects.list_item_1`
- `objects.list_item_2`
- `objects.list_item_3`
- `objects.list_item_4`
- `objects.list_item_5`
- `objects.list_item_6`

Поведение:

- При входе загрузить список работников через `DeviceApi::loadWorkers()`.
- Показать по 6 ФИО на страницу.
- Для каждой строки сохранить выбранного работника.
- Если `offset == 0`, скрыть `List_Back`.
- Если работников меньше 7 или следующей страницы нет, скрыть `List_Next`.
- При нажатии на ФИО открыть `Number`.

Вопрос: при ошибке загрузки работников показываем `Load` с текстом ошибки, отдельный `Error`, или остаемся на `List` с пустым списком и сообщением?

### 7. Number

Файлы:

- `src/Screen/Page/Main/Number.h`
- `src/Screen/Page/Main/Number.cpp`

EEZ-объекты:

- `objects.kbd_text`
- `objects.kbd_key`

Поведение:

- Отображать ввод PIN/пароля для выбранного работника.
- Отмена возвращает на `List`.
- Принять отправляет login/password в `DeviceApi::login()`.
- При успешном login открыть `Process`.
- При ошибке очистить поле и показать ошибку понятным способом.

Проблема:

- Сейчас `KBD_KEY` является стандартной `lv_keyboard`, выглядит как калькулятор/клавиатура.
- В сгенерированных `actions.h` есть только `action_keyboard_text` и `action_keyboard_number`.

Варианты решения:

1. В EEZ заменить `KBD_KEY` на набор обычных кнопок `0..9`, `OK`, `Cancel`, `Backspace`. Это самый управляемый вариант.
2. Оставить `lv_keyboard`, но в коде настроить режим, карту клавиш и callbacks. Это быстрее, но хуже контролируется визуально.

Вопрос: можно ли менять EEZ-проект для экрана `Number`, или пока надо решить только C++-кодом поверх текущего `lv_keyboard`?

### 8. Process

Файлы:

- `src/Screen/Page/Main/Process.h`
- `src/Screen/Page/Main/Process.cpp`

EEZ-объекты:

- `objects.process_title`
- `objects.process_fio`
- `objects.process_count`
- `objects.process_status`
- `objects.process_details`
- `objects.process_close`

Поведение:

- `Process_Title`: номер смены, вероятно `workID`.
- `Process_FIO`: ФИО сотрудника.
- `Process_Count`: максимальный номер детали за смену.
- `Process_Status`: состояние последней детали.
- `Process_Details`: открыть `Details`.
- `Process_Close`: отправить logout, затем перезагрузить ESP32 или вернуться к загрузке/списку.

Вопрос: `Process_Close` должен всегда делать `ESP.restart()` после logout, или при ошибке logout не перезагружать устройство?

### 9. Details

Файлы:

- `src/Screen/Page/Main/Details.h`
- `src/Screen/Page/Main/Details.cpp`

EEZ-объекты:

- `objects.details_back`
- `objects.details_next`
- `objects.details_param1..6`
- `objects.details_value1..6`
- `objects.details_value1_1..details_value6_1`

Поведение:

- Показать 6 деталей на страницу.
- `Details_Param`: номер детали.
- `Details_Value`: состояние детали.
- `Details_Time`: время создания детали. В текущем `screens.h` это сгенерировано как `details_valueX_1`, нужно использовать эти имена как поле времени.
- Листание аналогично `List`.
- `Details_Back` имеет двойной смысл: если это кнопка листания назад, нужна отдельная кнопка возврата на `Process`; если это кнопка возврата на предыдущую страницу, тогда для листания назад нужен другой объект.

Вопрос: `Details_Back` должен листать детали назад или возвращать на `Process`? В описании сказано листать, но тогда не указан способ выйти обратно на `Process`.

## Порядок реализации

1. Перевести `Panel` и `Page` на EEZ-generated UI.
2. Добавить helper для текста внутри кнопок и скрытия объектов.
3. Добавить `Load` на EEZ-экран и версию в `Config`.
4. Создать `DeviceApi` и структуры работников/сессии.
5. Реализовать `List` с пагинацией и выбором работника.
6. Реализовать `Number` с текущей клавиатурой или после правки EEZ-проекта.
7. Реализовать `Process`.
8. Реализовать `Details` на локальном списке деталей.
9. Собрать `pio run`.
10. Проверить `WEB` API, если потребуется добавить `login` или endpoint списка деталей.

## Проверки

- `pio run` в `ESP32`.
- Проверить, что `ui_init()` вызывается один раз.
- Проверить, что на все кликабельные кнопки обработчики вешаются один раз.
- Проверить скрытие `Back/Next` на списках 0, 1, 6, 7, 12, 13 элементов.
- Проверить, что пустые строки списка скрываются и не кликаются.
- Проверить, что после logout сессия очищается в `Data`.

## Открытые вопросы перед кодом

1. Используем `userID` вместо `login`, или добавляем поле `login` в `WEB /api/device/workers`?
2. Для `Details` нужен новый WEB endpoint получения деталей, или пока показываем только локально накопленные события?
3. Можно ли править EEZ-проект для нормального цифрового PIN-пада на `Number`?
4. Как показывать ошибки API пользователю: отдельный экран, текст на текущем экране или временное сообщение?
5. После `Process_Close`: всегда `ESP.restart()` или только после успешного logout?
6. Как выйти с `Details` обратно на `Process`, если `Details_Back` используется для листания назад?
