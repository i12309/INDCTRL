"""Точка входа event-service."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from control_common.config import get_settings
from control_common.constants import SERVICE_EVENT
from control_common.db import close_connection_pool, init_connection_pool
from control_common.logging import configure_logging

configure_logging()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Подготовить и закрыть общие ресурсы FastAPI-приложения."""

    init_connection_pool(settings=get_settings())
    try:
        yield
    finally:
        close_connection_pool()


app = FastAPI(
    title="INDCTRL Event Service",
    description="Сервис приема событий о произведенных деталях от ESP32.",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(router)


@app.get("/", tags=["service"])
def root() -> dict[str, str]:
    """Вернуть краткую информацию о сервисе."""

    return {"service": SERVICE_EVENT}
