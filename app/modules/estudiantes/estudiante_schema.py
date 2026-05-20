from datetime import date
from typing import Optional

from pydantic import BaseModel


class EstudianteEncontradoDTO(BaseModel):
    id_estudiante: int
    nombres: str
    paterno: str
    materno: Optional[str] = None
    id_colegio: int
    carnet_identidad: str
    curso: int
    nivel: str
    fecha_nacimiento: date
    rude: Optional[str] = None
    telefono: Optional[int] = None
    correo: Optional[str] = None


class EstudianteUpdateDTO(BaseModel):
    nombres: Optional[str] = None
    paterno: Optional[str] = None
    materno: Optional[str] = None
    id_colegio: Optional[int] = None
    curso: Optional[int] = None
    nivel: Optional[str] = None
    rude: Optional[str] = None
    telefono: Optional[int] = None
    correo: Optional[str] = None
