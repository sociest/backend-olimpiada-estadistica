from pydantic import BaseModel, ConfigDict

from app.modules.auth.auth_model import EstadoAdministrador

class AdministradorCreateDTO(BaseModel):
    nombre: str
    correo: str
    contrasena: str


class AdministradorUpdateDTO(BaseModel):
    nombre: str | None = None
    correo: str | None = None


class AdministradorResponseDTO(BaseModel):
    id_administrador: int
    nombre: str
    correo: str
    estado: EstadoAdministrador

    model_config = ConfigDict(from_attributes=True)
