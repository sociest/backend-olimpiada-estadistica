from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MaterialCreateDTO(BaseModel):
    nombre_material: str
    descripcion: Optional[str] = None
    tipo_material: str
    fecha_publicacion: Optional[datetime] = None
    id_convocatoria: Optional[int] = None
    id_categoria: Optional[int] = None
    id_fase: Optional[int] = None


class MaterialUpdateDTO(BaseModel):
    nombre_material: Optional[str] = None
    descripcion: Optional[str] = None
    tipo_material: Optional[str] = None
    fecha_publicacion: Optional[datetime] = None
    id_convocatoria: Optional[int] = None
    id_categoria: Optional[int] = None
    id_fase: Optional[int] = None


class MaterialResponseDTO(BaseModel):
    id_material: int
    nombre_material: str
    enlace_acceso: str
    descripcion: Optional[str] = None
    fecha_creacion: datetime
    estado: str
    tipo_material: str
    fecha_publicacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
