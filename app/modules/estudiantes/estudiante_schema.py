from datetime import date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

from app.modules.categorias.categoria_model import NivelEducativo
from app.modules.colegios.colegio_model import TurnoColegio
from app.modules.personas.persona_model import EstadoPersona

class ColegioMinimoDTO(BaseModel):
    id_colegio: int
    nombre: str
    turno: TurnoColegio
    model_config = ConfigDict(from_attributes=True)

class EstudianteBaseDTO(BaseModel):
    id_colegio: int
    carnet_identidad: str
    curso: int
    nivel: NivelEducativo
    fecha_nacimiento: date
    rude: Optional[str] = None
    telefono: Optional[str] = None
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
    nivel: Optional[NivelEducativo] = None
    rude: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None

class EstudianteEstadoUpdateDTO(BaseModel):
    estado: EstadoPersona

class EstudianteResponseDTO(EstudianteBaseDTO):
    id_estudiante: int
    nombres: str
    paterno: str
    materno: Optional[str] = None
    estado: EstadoPersona
    colegio: Optional[ColegioMinimoDTO] = None

    model_config = ConfigDict(from_attributes=True)

class ExportarEstudiantesDTO(BaseModel):
    ids: List[int]
