from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ColegioNuevoDTO(BaseModel):
    codigo: int
    nombre: str
    tipo: str
    turno: str
    departamento: str
    municipio: str
    calle: Optional[str] = None
    numero: Optional[str] = None


class EstudianteFormularioDTO(BaseModel):
    nombres: str
    paterno: str
    materno: Optional[str] = None
    carnet_identidad: str
    fecha_nacimiento: date
    curso: int
    nivel: str
    rude: Optional[str] = None
    telefono: Optional[int] = None
    correo: Optional[str] = None


class InscripcionFormularioDTO(BaseModel):
    id_convocatoria: int
    id_categoria: int
    estudiante: EstudianteFormularioDTO
    id_colegio: Optional[int] = None
    colegio_nuevo: Optional[ColegioNuevoDTO] = None


class InscripcionResponseDTO(BaseModel):
    id_inscripcion: int
    id_estudiante: int
    id_convocatoria: int
    id_categoria: int
    fecha_inscripcion: datetime
    estado: str

    model_config = ConfigDict(from_attributes=True)


class InscripcionFormularioResponseDTO(BaseModel):
    inscripcion: InscripcionResponseDTO
    estudiante: dict
    colegio: dict
