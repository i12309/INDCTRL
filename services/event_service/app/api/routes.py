"""HTTP-маршруты event-service."""

from fastapi import APIRouter, Request

from app.schemas.responses import ErrorResponse, HealthResponse, StatusResponse
from app.services.event_service import EventService
from control_common.errors import AppError

router = APIRouter()
event_service = EventService()


@router.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    """Проверить, что контейнер event-service запущен и отвечает."""

    return event_service.health()


@router.get("/api/events/health", response_model=HealthResponse, tags=["health"])
def api_health() -> HealthResponse:
    """Проверить event-service через общий Nginx-префикс `/api/events`."""

    return event_service.health()


@router.post("/api/events/detail", response_model=StatusResponse | ErrorResponse, tags=["events"])
async def detail_event(request: Request) -> StatusResponse | ErrorResponse:
    """Принять событие произведенной детали от ESP32."""

    raw_body = await request.body()
    source_ip = request.client.host if request.client else None

    try:
        return event_service.handle_raw_detail_event(raw_body, source_ip=source_ip)
    except AppError as exc:
        return ErrorResponse(success=False, error=exc.message)
