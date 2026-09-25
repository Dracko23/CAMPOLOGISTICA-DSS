from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    id_usuario: int
    email: str
    nombre: str
    rol: str
    id_conductor: int | None = None
    id_cliente: int | None = None

    class Config:
        from_attributes = True


class MeResponse(BaseModel):
    id_usuario: int
    email: str
    nombre: str
    rol: str
    id_conductor: int | None = None
    id_cliente: int | None = None

    class Config:
        from_attributes = True