from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AuthenticationError, ConflictError, UnauthorizedError, ValidationError
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.auth.auth_model import AdministradorModel
from app.modules.auth.auth_repository import AuthRepository
from app.modules.auth.auth_schema import AdminCreateDTO, LoginDTO


class AuthService:
    def __init__(self, db: Session):
        self.repository = AuthRepository(db)

    def login(self, data: LoginDTO):
        admin = self.repository.get_admin_by_correo(data.correo)
        if not admin or not verify_password(data.contrasena, admin.contrasena):
            raise AuthenticationError("Credenciales invalidas")

        access_token = create_access_token(admin.id_administrador)
        self.repository.create_auditoria(
            admin_id=admin.id_administrador,
            accion="LOGIN",
            descripcion="Login exitoso",
        )

        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
            "usuario": admin,
        }

    def create_admin(self, data: AdminCreateDTO, current_admin_id: int | None = None):
        has_admins = self.repository.count_admins() > 0
        if has_admins and current_admin_id is None:
            raise UnauthorizedError("No autorizado")

        if len(data.contrasena) < 8:
            raise ValidationError("La contrasena debe tener al menos 8 caracteres")

        existing_admin = self.repository.get_admin_by_correo(data.correo)
        if existing_admin:
            raise ConflictError("El correo ya esta registrado")

        admin = AdministradorModel(
            nombre=data.nombre,
            correo=data.correo,
            contrasena=hash_password(data.contrasena),
        )
        created_admin = self.repository.create_admin(admin)

        if current_admin_id is not None:
            self.repository.create_auditoria(
                admin_id=current_admin_id,
                accion="CREAR_ADMINISTRADOR",
                descripcion=f"Administrador creado: {created_admin.correo}",
            )

        return created_admin

    def logout(self, admin_id: int):
        self.repository.create_auditoria(
            admin_id=admin_id,
            accion="LOGOUT",
            descripcion="Logout exitoso",
        )
        return {"logout": True}
