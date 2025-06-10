# src/api/middleware.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
import logging
from typing import Callable, Awaitable
from http import HTTPStatus

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base exception for API errors"""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)

async def error_middleware(request: Request, call_next: Callable[[Request], Awaitable]):
    """Global error handling middleware"""
    try:
        return await call_next(request)
    except APIError as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "error": {
                    "message": e.message,
                    "code": e.error_code or f"HTTP_{e.status_code}",
                    "status": HTTPStatus(e.status_code).phrase
                }
            }
        )
    except Exception as e:
        logger.exception("Unhandled exception in API")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "message": "An unexpected error occurred",
                    "code": "INTERNAL_SERVER_ERROR",
                    "status": "Internal Server Error"
                }
            }
        )