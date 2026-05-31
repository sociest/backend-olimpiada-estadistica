from pydantic import BaseModel, ConfigDict

from app.modules.auth.auth_model import EstadoAdministrador

class LoginDTO(BaseModel):
    correo: str
    contrasena: str


class AdminCreateDTO(BaseModel):
    nombre: str
    correo: str
    contrasena: str


class UsuarioAutenticadoDTO(BaseModel):
    id_administrador: int
    nombre: str
    correo: str
    estado: EstadoAdministrador

    model_config = ConfigDict(from_attributes=True)


class TokenDataDTO(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    usuario: UsuarioAutenticadoDTO


class LogoutResponseDTO(BaseModel):
    logout: bool


class CambiarContrasenaDTO(BaseModel):
    contrasena_actual: str
    nueva_contrasena: str
    repetir_nueva_contrasena: str


class CambiarContrasenaResponseDTO(BaseModel):
    actualizado: bool
