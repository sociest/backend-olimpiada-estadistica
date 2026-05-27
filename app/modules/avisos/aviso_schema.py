from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AvisoCreateDTO(BaseModel):
    titulo: str
    descripcion: str
    tipo: str
    fecha_publicacion: Optional[datetime] = None


class AvisoUpdateDTO(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    tipo: Optional[str] = None
    fecha_publicacion: Optional[datetime] = None


class AvisoResponseDTO(BaseModel):
    id_aviso: int
    titulo: str
    descripcion: str
    tipo: str
    fecha_creacion: datetime
    fecha_publicacion: Optional[datetime] = None
    estado: str

    model_config = ConfigDict(from_attributes=True)
