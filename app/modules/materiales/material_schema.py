from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.modules.materiales.material_model import EstadoMaterial, EstadoTemporalMaterial, TipoMaterialEnum


class MaterialBaseDTO(BaseModel):
    nombre_material: str
    descripcion: Optional[str] = None
    tipo_material: TipoMaterialEnum
    fecha_publicacion: Optional[datetime] = None


class MaterialExternoCreateDTO(MaterialBaseDTO):
    enlace_acceso: str


class MaterialUpdateDTO(BaseModel):
    nombre_material: Optional[str] = None
    descripcion: Optional[str] = None
    tipo_material: Optional[TipoMaterialEnum] = None
    fecha_publicacion: Optional[datetime] = None
    enlace_acceso: Optional[str] = None


class RelacionConvocatoriaDTO(BaseModel):
    id_convocatoria: int
    nombre_convocatoria: str
    gestion: int
    model_config = ConfigDict(from_attributes=True)


class RelacionFaseDTO(BaseModel):
    id_fase: int
    nombre_fase: str
    nombre_categoria: str
    model_config = ConfigDict(from_attributes=True)


class MaterialResponseDTO(BaseModel):
    id_material: int
    nombre_material: str
    enlace_acceso: str
    descripcion: Optional[str]
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    estado: EstadoMaterial
    estado_temporal: EstadoTemporalMaterial
    tipo_material: TipoMaterialEnum
    fecha_publicacion: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class MaterialDetalleResponseDTO(MaterialResponseDTO):
    convocatorias: List[RelacionConvocatoriaDTO] = []
    fases: List[RelacionFaseDTO] = []

class MaterialPublicoGeneralDTO(BaseModel):
    nombre_material: str
    enlace_acceso: str
    descripcion: Optional[str] = None
    fecha_publicacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class MaterialPublicoRelacionDTO(BaseModel):
    nombre_material: str
    descripcion: Optional[str] = None
    enlace_acceso: str
    tipo_material: TipoMaterialEnum

    model_config = ConfigDict(from_attributes=True)

class MaterialPublicoDTO(BaseModel):
    nombre: str
    enlace_acceso: str

    model_config = ConfigDict(from_attributes=True)

class MaterialesInicioDTO(BaseModel):
    afiche: Optional[MaterialPublicoDTO] = None
    convocatoria: Optional[MaterialPublicoDTO] = None

class MaterialesDetalleDTO(MaterialesInicioDTO):
    reglamento: Optional[MaterialPublicoDTO] = None