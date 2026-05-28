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
    estudiante: EstudianteFormularioDTO
    id_colegio: int

class InscripcionFormularioRequestDTO(InscripcionFormularioDTO):
    username_hp: str = ""
    cf_turnstile_response: str = ""

class EstudianteBuscarDTO(BaseModel):
    carnet_identidad: str
    fecha_nacimiento: date

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
    ya_inscrito: bool = False
    id_inscripcion: Optional[int] = None
    restriccion_edad: Optional[str] = None

class ColegioMinimoDTO(BaseModel):
    nombre: str
    tipo: str
    turno: str
    calle: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True) # <-- SOLUCIÓN

class CategoriaMinimaDTO(BaseModel):
    id_categoria: int
    nombre_categoria: str
    
    model_config = ConfigDict(from_attributes=True) # <-- SOLUCIÓN

class EstudianteMinimoDTO(BaseModel):
    id_estudiante: int
    nombres: str
    paterno: str
    materno: Optional[str] = None
    carnet_identidad: str
    rude: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True) # <-- SOLUCIÓN

class InscripcionResponseDTO(BaseModel):
    id_inscripcion: int
    id_estudiante: int
    id_convocatoria: int
    id_categoria: int
    fecha_inscripcion: datetime
    estado: str
    estudiante: Optional[EstudianteMinimoDTO] = None
    categoria: Optional[CategoriaMinimaDTO] = None

    model_config = ConfigDict(from_attributes=True)

class InscripcionFormularioResponseDTO(BaseModel):
    inscripcion: InscripcionResponseDTO
    estudiante: dict
    colegio: dict

class InscripcionAdminCreateDTO(BaseModel):
    id_estudiante: int
    id_convocatoria: int
    id_categoria: int

class InscripcionEstadoUpdateDTO(BaseModel):
    estado: str

class ExportarInscripcionesRequestDTO(BaseModel):
    id_inscripciones: list[int]