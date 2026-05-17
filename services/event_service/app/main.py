"""Точка входа event-service."""

from fastapi import FastAPI

from app.api.routes import router
from control_common.constants import SERVICE_EVENT
from control_common.logging import configure_logging

configure_logging()

app = FastAPI(
    title="INDCTRL Event Service",
    description="Сервис приема событий о произведенных деталях от ESP32.",
    version="0.1.0",
)
app.include_router(router)


@app.get("/", tags=["service"])
def root() -> dict[str, str]:
    """Вернуть краткую информацию о сервисе."""

    return {"service": SERVICE_EVENT}
