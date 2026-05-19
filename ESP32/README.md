# INDCTRL ESP32

Empty PlatformIO/Arduino project for the INDCTRL ESP32 front panel.

The hardware target and display stack are based on `Harvester32/Front32`:

- board: `JC8048W550C`
- display: 800x480 LVGL through `esp32-smartdisplay`
- local libraries: `lib/esp32-smartdisplay`, `lib/lvgl`

Current source layout:

- `src/App` - composition root and main loop facade
- `src/Screen` - LVGL panel and page classes
- `src/Screen/Page/Main` - only the Main page family copied as empty placeholders
- `src/Service` - reusable services and API placeholders
- `src/State` - minimal state machine ready for business states

Build:

```bash
pio run
```
