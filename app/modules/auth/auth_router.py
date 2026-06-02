from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.dependencies import bearer_scheme, get_current_admin, limiter, verify_bot_protection
from app.core.exceptions import UnauthorizedError
from app.core.responses import ResponseBase
from app.core.security import decode_access_token
from app.db.database import get_db
from app.modules.auth.auth_repository import AuthRepository
from app.modules.auth.auth_model import EstadoAdministrador
from app.modules.auth.auth_schema import (
    AdminCreateDTO,
    CambiarContrasenaDTO,
    CambiarContrasenaResponseDTO,
    LoginDTO,
    LogoutResponseDTO,
    TokenDataDTO,
    UsuarioAutenticadoDTO,
)
from app.modules.auth.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=ResponseBase[TokenDataDTO])
@limiter.limit("5/minute")
async def login(
    request: Request,
    data: LoginDTO,
    db: Session = Depends(get_db),
):
    await verify_bot_protection(
        cf_turnstile_response=data.cf_turnstile_response,
        username_hp=data.username_hp,
        client_ip=request.client.host,
    )
    client_ip = (request.headers.get("CF-Connecting-IP") or request.client.host)
    service = AuthService(db)
    token_data = service.login(data, client_ip=client_ip)
    return ResponseBase(
        data=token_data,
        message="Autenticacion exitosa"
    )

@router.post("/admins", response_model=ResponseBase[UsuarioAutenticadoDTO])
def registrar_admin(
    data: AdminCreateDTO,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
):
    current_admin_id = _get_optional_current_admin_id(credentials, db)
    service = AuthService(db)
    admin = service.create_admin(data, current_admin_id=current_admin_id)
    return ResponseBase(data=admin, message="Administrador registrado correctamente")


@router.get("/me", response_model=ResponseBase[UsuarioAutenticadoDTO])
def obtener_usuario_logueado(
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin),
):
    service = AuthService(db)
    admin = service.get_current_user(admin_id)
    return ResponseBase(data=admin, message="Usuario autenticado")


@router.patch("/me/password", response_model=ResponseBase[CambiarContrasenaResponseDTO])
def cambiar_contrasena(
    data: CambiarContrasenaDTO,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_admin),
):
    service = AuthService(db)
    result = service.cambiar_contrasena(admin_id, data)
    return ResponseBase(data=result, message="Contrasena actualizada correctamente")


@router.post("/logout", response_model=ResponseBase[LogoutResponseDTO])
def logout(db: Session = Depends(get_db), admin_id: int = Depends(get_current_admin)):
    service = AuthService(db)
    result = service.logout(admin_id)
    return ResponseBase(data=result, message="Logout exitoso")


def _get_optional_current_admin_id(
    credentials: HTTPAuthorizationCredentials | None,
    db: Session,
) -> int | None:
    repository = AuthRepository(db)
    if repository.count_admins() == 0:
        return None

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("No autorizado")

    payload = decode_access_token(credentials.credentials)
    admin_id = payload.get("sub")
    if admin_id is None:
        raise UnauthorizedError("Token invalido")

    admin = repository.get_admin_by_id(int(admin_id))
    if not admin or admin.estado != EstadoAdministrador.ACTIVO:
        raise UnauthorizedError("No autorizado")

    return admin.id_administrador
