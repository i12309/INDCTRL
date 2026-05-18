"""Доменные константы Django-приложения INDCTRL."""

SERVICE_INDCTRL = "indctrl"
DEFAULT_HEALTH_STATUS = "ok"

PERM_VIEW_REPORTS = "accounts.view_reports"
PERM_USE_ESP32_API = "accounts.use_esp32_api"

WORK_STATUS_ACTIVE = "active"
WORK_STATUS_FINISHED = "finished"
WORK_STATUS_EXPIRED = "expired"
WORK_STATUS_CANCELLED = "cancelled"

DETAIL_STATE_WORKING = "working"
DETAIL_STATE_DEFECT = "defect"
DETAIL_STATE_UNDEFINED = "undefined"
