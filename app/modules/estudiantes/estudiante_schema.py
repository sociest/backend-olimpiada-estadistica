from datetime import date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class ColegioMinimoDTO(BaseModel):
    id_colegio: int
    nombre: str
    
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

class EstudianteEstadoUpdateDTO(BaseModel):
    estado: str

class EstudianteResponseDTO(EstudianteBaseDTO):
    id_estudiante: int
    nombres: str
    paterno: str
    materno: Optional[str] = None
    estado: str
    colegio: Optional[ColegioMinimoDTO] = None

    model_config = ConfigDict(from_attributes=True)

class ExportarEstudiantesDTO(BaseModel):
    ids: List[int]