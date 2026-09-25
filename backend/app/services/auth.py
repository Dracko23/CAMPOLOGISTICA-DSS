from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.models import Usuario
from app.schemas.auth import LoginRequest, MeResponse, TokenResponse, UserResponse


class AuthService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def authenticate(self, payload: LoginRequest) -> TokenResponse:
        usuario = self.session.scalar(select(Usuario).where(Usuario.email == payload.email))
        if not usuario or not usuario.activo:
            raise UnauthorizedError("credenciales_invalidas", "Credenciales incorrectas.")
        if not verify_password(payload.password, usuario.password_hash):
            raise UnauthorizedError("credenciales_invalidas", "Credenciales incorrectas.")
        token = create_access_token({"sub": str(usuario.id_usuario), "rol": usuario.rol})
        return TokenResponse(
            access_token=token,
            user=UserResponse.model_validate(usuario),
        )

    def get_current_user(self, user_id: int) -> MeResponse:
        usuario = self.get_user_model(user_id)
        return MeResponse.model_validate(usuario)

    def get_user_model(self, user_id: int) -> Usuario:
        usuario = self.session.get(Usuario, user_id)
        if not usuario or not usuario.activo:
            raise UnauthorizedError("usuario_no_encontrado", "Usuario no encontrado o inactivo.")
        return usuario

    def create_user(
        self,
        *,
        email: str,
        password: str,
        rol: str,
        nombre: str,
        id_conductor: int | None = None,
        id_cliente: int | None = None,
    ) -> Usuario:
        usuario = Usuario(
            email=email,
            password_hash=hash_password(password),
            rol=rol,
            nombre=nombre,
            activo=True,
            id_conductor=id_conductor,
            id_cliente=id_cliente,
            fecha_creacion=__import__("datetime").datetime.now(),
        )
        self.session.add(usuario)
        self.session.commit()
        self.session.refresh(usuario)
        return usuario
