"""HTTP-маршруты auth-service."""

from fastapi import APIRouter

from app.schemas.requests import DeviceWorkersRequest, LoginRequest, SessionRequest
from app.schemas.responses import (
    DeviceWorkersResponse,
    ErrorResponse,
    HealthResponse,
    LoginResponse,
    StatusResponse,
)
from app.services.auth_service import AuthService
from control_common.errors import AppError

router = APIRouter()
auth_service = AuthService()


@router.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    """Проверить, что контейнер auth-service запущен и отвечает."""

    return auth_service.health()


@router.get("/api/auth/health", response_model=HealthResponse, tags=["health"])
def api_health() -> HealthResponse:
    """Проверить auth-service через общий Nginx-префикс `/api/auth`."""

    return auth_service.health()


@router.post(
    "/api/auth/device/workers",
    response_model=DeviceWorkersResponse | ErrorResponse,
    tags=["auth"],
)
def device_workers(request: DeviceWorkersRequest) -> DeviceWorkersResponse | ErrorResponse:
    """Вернуть список работников, доступных на станке ESP32."""

    try:
        return auth_service.get_workers_for_device(request.mac_address)
    except AppError as exc:
        return ErrorResponse(success=False, error=exc.message)


@router.post("/api/auth/login", response_model=LoginResponse | ErrorResponse, tags=["auth"])
def login(request: LoginRequest) -> LoginResponse | ErrorResponse:
    """Авторизовать работника на станке и создать рабочую смену."""

    try:
        return auth_service.login(
            user_id=request.user_id,
            password=request.password,
            mac_address=request.mac_address,
        )
    except AppError as exc:
        return ErrorResponse(success=False, error=exc.message)


@router.post("/api/auth/logout", response_model=StatusResponse | ErrorResponse, tags=["auth"])
def logout(request: SessionRequest) -> StatusResponse | ErrorResponse:
    """Завершить смену по активной сессии."""

    try:
        return auth_service.logout(request.session_id)
    except AppError as exc:
        return ErrorResponse(success=False, error=exc.message)


@router.post("/api/auth/heartbeat", response_model=StatusResponse | ErrorResponse, tags=["auth"])
def heartbeat(request: SessionRequest) -> StatusResponse | ErrorResponse:
    """Обновить heartbeat активной смены."""

    try:
        return auth_service.heartbeat(request.session_id)
    except AppError as exc:
        return ErrorResponse(success=False, error=exc.message)
