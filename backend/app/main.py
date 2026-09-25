from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.v1 import router as api_v1_router
from app.core.config import get_settings
from app.core.errors import AppError, app_error_handler

settings = get_settings()
app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list({
        str(settings.frontend_origin).rstrip("/"),
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    }),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(api_v1_router)
app.add_exception_handler(AppError, app_error_handler)
