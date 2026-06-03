from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.modules.avisos.aviso_model import AvisoPrioridad, EstadoAviso, TipoAviso

class AvisoCreateDTO(BaseModel):
    titulo: str
    descripcion: str
    tipo: TipoAviso
    prioridad: AvisoPrioridad = AvisoPrioridad.MEDIA
    fecha_publicacion: Optional[datetime] = None

class AvisoUpdateDTO(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    tipo: Optional[TipoAviso] = None
    prioridad: Optional[AvisoPrioridad] = None
    fecha_publicacion: Optional[datetime] = None

class AvisoEstadoUpdateDTO(BaseModel):
    estado: EstadoAviso

class AvisoResponseDTO(BaseModel):
    id_aviso: int
    titulo: str
    descripcion: str
    tipo: TipoAviso
    prioridad: AvisoPrioridad
    fecha_creacion: datetime
    fecha_publicacion: Optional[datetime] = None
    estado: EstadoAviso
    estado_temporal: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class AvisoPublicoDTO(BaseModel):
    prioridad: str
    titulo: str
    descripcion: str
    tipo: TipoAviso