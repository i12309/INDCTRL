"""HTTP-маршруты event-service."""

from fastapi import APIRouter

from app.schemas.responses import HealthResponse
from app.services.event_service import EventService

router = APIRouter()
event_service = EventService()


@router.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    """Проверить, что контейнер event-service запущен и отвечает."""

    return event_service.health()
