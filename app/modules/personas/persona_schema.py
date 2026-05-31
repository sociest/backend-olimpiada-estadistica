from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.modules.personas.persona_model import EstadoPersona, TipoColaborador

class PersonaBaseDTO(BaseModel):
    nombres: str
    paterno: str
    materno: Optional[str] = None


class PersonaCreateDTO(PersonaBaseDTO):
    pass


class PersonaResponseDTO(PersonaBaseDTO):
    id_persona: int

    model_config = ConfigDict(from_attributes=True)

class DirectorBaseDTO(BaseModel):
    id_colegio: Optional[int] = None
    telefono_1: Optional[str] = None
    telefono_2: Optional[str] = None


class DirectorCreateDTO(DirectorBaseDTO):
    nombres: str
    paterno: str
    materno: Optional[str] = None


class DirectorResponseDTO(DirectorBaseDTO):
    id_director: int
    nombres: str
    paterno: str
    materno: Optional[str] = None
    estado: Optional[EstadoPersona] = None

    model_config = ConfigDict(from_attributes=True)


class ColaboradorBaseDTO(BaseModel):
    presentacion: Optional[str] = None
    rol: str
    tipo: TipoColaborador
    correo: str

class ColaboradorCreateDTO(ColaboradorBaseDTO):
    nombres: str
    paterno: str
    materno: Optional[str] = None

class ColaboradorUpdateDTO(BaseModel):
    nombres: Optional[str] = None
    paterno: Optional[str] = None
    materno: Optional[str] = None
    presentacion: Optional[str] = None
    rol: Optional[str] = None
    tipo: Optional[TipoColaborador] = None
    correo: Optional[str] = None

class ColaboradorResponseDTO(ColaboradorBaseDTO):
    id_colaborador: int
    nombres: str
    paterno: str
    materno: Optional[str] = None
    perfil: Optional[str] = None
    estado: EstadoPersona

    model_config = ConfigDict(from_attributes=True)
    
class DirectorUpdateDTO(BaseModel):
    id_colegio: Optional[int] = None # Si envías explicitamente None, lo desliga
    telefono_1: Optional[str] = None
    telefono_2: Optional[str] = None
    nombres: Optional[str] = None
    paterno: Optional[str] = None
    materno: Optional[str] = None
class DirectorMinifiedDTO(BaseModel):
    id_director: int
    nombres_completos: str
