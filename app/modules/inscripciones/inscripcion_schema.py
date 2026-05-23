from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

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
    id_colegio: int

# DTO de Petición con campos de seguridad
class InscripcionFormularioRequestDTO(InscripcionFormularioDTO):
    username_hp: str = ""
    cf_turnstile_response: str = ""

class EstudianteBuscarDTO(BaseModel):
    carnet_identidad: str
    fecha_nacimiento: date

# DTO de Petición con campos de seguridad
class EstudianteBuscarRequestDTO(EstudianteBuscarDTO):
    username_hp: str = ""
    cf_turnstile_response: str = ""

class EstudianteBusquedaResponseDTO(BaseModel):
    id_estudiante: int
    nombres: str
    paterno: str
    materno: Optional[str] = None
    carnet_identidad: str
    fecha_nacimiento: date
    curso: Optional[int] = None
    nivel: Optional[str] = None
    rude: Optional[str] = None
    telefono: Optional[int] = None
    correo: Optional[str] = None
    id_colegio: Optional[int] = None

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