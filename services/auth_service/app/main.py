"""Точка входа auth-service."""

from fastapi import FastAPI

from app.api.routes import router
from control_common.constants import SERVICE_AUTH
from control_common.logging import configure_logging

configure_logging()

app = FastAPI(
    title="INDCTRL Auth Service",
    description="Сервис авторизации работников на ESP32-терминалах.",
    version="0.1.0",
)
app.include_router(router)


@app.get("/", tags=["service"])
def root() -> dict[str, str]:
    """Вернуть краткую информацию о сервисе."""

    return {"service": SERVICE_AUTH}
