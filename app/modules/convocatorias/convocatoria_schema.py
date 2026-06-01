from datetime import date, datetime
from typing import Optional
from decimal import Decimal 
from pydantic import BaseModel, ConfigDict, Field
from typing import List
from app.modules.convocatorias.convocatoria_model import EstadoConvocatoria, EstadoTemporal
from app.modules.categorias.categoria_schema import CategoriaDetalleDTO, CategoriaInicioDTO
from app.modules.materiales.material_schema import MaterialesInicioDTO,MaterialesDetalleDTO
class ConvocatoriaBaseDTO(BaseModel):
    nombre_convocatoria: str
    gestion: int = Field(..., ge=2024)
    descripcion: Optional[str] = None
    inicio_olimpiadas: Optional[date] = None
    fin_olimpiadas: Optional[date] = None
    fecha_inicio_inscripcion: Optional[datetime] = None
    fecha_fin_inscripcion: Optional[datetime] = None
    monto_inscripcion: Optional[float] = Field(None, ge=0)


class ConvocatoriaCreateDTO(ConvocatoriaBaseDTO):
    pass


class ConvocatoriaUpdateDTO(BaseModel):
    nombre_convocatoria: Optional[str] = None
    gestion: Optional[int] = Field(None, ge=2024)
    descripcion: Optional[str] = None
    inicio_olimpiadas: Optional[date] = None
    fin_olimpiadas: Optional[date] = None
    fecha_inicio_inscripcion: Optional[datetime] = None
    fecha_fin_inscripcion: Optional[datetime] = None
    monto_inscripcion: Optional[float] = Field(None, ge=0)


class ConvocatoriaResponseDTO(ConvocatoriaBaseDTO):
    id_convocatoria: int
    estado: EstadoConvocatoria
    estado_temporal: EstadoTemporal
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    model_config = ConfigDict(from_attributes=True)

class ConvocatoriaIdDTO(BaseModel):
    id_convocatoria: int

class ConvocatoriaInicioDTO(BaseModel):
    id_convocatoria: int
    nombre_convocatoria: str
    gestion: int
    descripcion: Optional[str] = None
    estado_temporal: str
    monto_inscripcion: Optional[Decimal] = None
    inicio_olimpiadas: Optional[date] = None
    fin_olimpiadas: Optional[date] = None
    fecha_inicio_inscripcion: Optional[datetime] = None
    fecha_fin_inscripcion: Optional[datetime] = None
    categorias: List[CategoriaInicioDTO] = []
    material_principal: MaterialesInicioDTO

class ConvocatoriaDetalleDTO(BaseModel):
    id_convocatoria: int
    nombre_convocatoria: str
    gestion: int
    descripcion: Optional[str] = None
    estado_temporal: str
    monto_inscripcion: Optional[Decimal] = None
    inicio_olimpiadas: Optional[date] = None
    fin_olimpiadas: Optional[date] = None
    fecha_inicio_inscripcion: Optional[datetime] = None
    fecha_fin_inscripcion: Optional[datetime] = None
    categorias: List[CategoriaDetalleDTO] = []
    material_principal: MaterialesDetalleDTO

class ConvocatoriaListPublicDTO(BaseModel):
    id_convocatoria: int
    nombre_convocatoria: str
    gestion: int
    descripcion: Optional[str] = None
    inicio_olimpiadas: Optional[date] = None
    fin_olimpiadas: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)