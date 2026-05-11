from pydantic import BaseModel, ConfigDict


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

    model_config = ConfigDict(from_attributes=True)


class TokenDataDTO(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    usuario: UsuarioAutenticadoDTO


class LogoutResponseDTO(BaseModel):
    logout: bool
