"""HTTP-маршруты auth-service."""

from fastapi import APIRouter

from app.schemas.responses import HealthResponse
from app.services.auth_service import AuthService

router = APIRouter()
auth_service = AuthService()


@router.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    """Проверить, что контейнер auth-service запущен и отвечает."""

    return auth_service.health()
