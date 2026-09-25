from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        field: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.field = field

    def detail(self) -> dict[str, Any]:
        value: dict[str, Any] = {'code': self.code, 'message': self.message}
        if self.field:
            value['field'] = self.field
        return value


class NotFoundError(AppError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(404, code, message)


class ConflictError(AppError):
    def __init__(self, code: str, message: str, field: str | None = None) -> None:
        super().__init__(409, code, message, field)


class UnauthorizedError(AppError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(401, code, message)


async def app_error_handler(_: Request, error: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content={'detail': error.detail()},
    )
