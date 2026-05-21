from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PersonaBaseDTO(BaseModel):
    nombres: str
    paterno: str
    materno: Optional[str] = None


class PersonaCreateDTO(PersonaBaseDTO):
    pass


class PersonaResponseDTO(PersonaBaseDTO):
    id_persona: int

    model_config = ConfigDict(from_attributes=True)


class EstudianteBaseDTO(BaseModel):
    id_colegio: int
    carnet_identidad: str
    curso: int
    nivel: str
    fecha_nacimiento: date
    rude: Optional[str] = None
    telefono: Optional[int] = None
    correo: Optional[str] = None


class EstudianteCreateDTO(EstudianteBaseDTO):
    nombres: str
    paterno: str
    materno: Optional[str] = None


class EstudianteResponseDTO(EstudianteBaseDTO):
    id_estudiante: int
    nombres: str
    paterno: str
    materno: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DirectorBaseDTO(BaseModel):
    id_colegio: Optional[int] = None
    telefono_1: str
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

    model_config = ConfigDict(from_attributes=True)


class ColaboradorBaseDTO(BaseModel):
    presentacion: Optional[str] = None
    rol: str
    tipo: str
    correo: str


class ColaboradorCreateDTO(ColaboradorBaseDTO):
    nombres: str
    paterno: str
    materno: Optional[str] = None


class ColaboradorResponseDTO(ColaboradorBaseDTO):
    id_colaborador: int
    nombres: str
    paterno: str
    materno: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
