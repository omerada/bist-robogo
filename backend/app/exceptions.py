# Source: Doc 07 §7 — Exception Handling + Doc 03 §3.2 (hata kodları)
"""Custom exception sınıfları ve global exception handler."""

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = structlog.get_logger()


# ── Custom Exception Sınıfları ──


class AppException(Exception):
    """Temel uygulama exception sınıfı."""

    def __init__(self, code: str, message: str, status_code: int = 400, details: dict | None = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class NotFoundException(AppException):
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} bulunamadı: {resource_id}",
            status_code=404,
        )


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Kimlik doğrulama gerekli"):
        super().__init__(code="UNAUTHORIZED", message=message, status_code=401)


class ForbiddenException(AppException):
    def __init__(self, message: str = "Bu işlem için yetkiniz yok"):
        super().__init__(code="FORBIDDEN", message=message, status_code=403)


class ConflictException(AppException):
    def __init__(self, message: str):
        super().__init__(code="CONFLICT", message=message, status_code=409)


class RiskLimitExceededException(AppException):
    def __init__(self, message: str, details: dict):
        super().__init__(
            code="RISK_LIMIT_EXCEEDED",
            message=message,
            status_code=422,
            details=details,
        )


class InsufficientBalanceException(AppException):
    def __init__(self, required: float, available: float):
        super().__init__(
            code="INSUFFICIENT_BALANCE",
            message="Yetersiz bakiye",
            status_code=422,
            details={"required": required, "available": available},
        )


class MarketClosedException(AppException):
    def __init__(self):
        super().__init__(
            code="MARKET_CLOSED",
            message="Piyasa şu anda kapalı",
            status_code=422,
        )


class BrokerException(AppException):
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(
            code="BROKER_ERROR",
            message=message,
            status_code=502,
            details=details or {},
        )


# ── Global Exception Handler'lar ──


def register_exception_handlers(app: FastAPI) -> None:
    """FastAPI uygulamasına global exception handler'ları ekler."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        logger.warning("app_exception", code=exc.code, message=exc.message, details=exc.details)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                },
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        errors = []
        for error in exc.errors():
            errors.append(
                {
                    "field": ".".join(str(loc) for loc in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"],
                }
            )
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "İstek doğrulama hatası",
                    "details": {"errors": errors},
                },
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("unhandled_exception", error=str(exc), exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Beklenmeyen bir hata oluştu",
                },
            },
        )
