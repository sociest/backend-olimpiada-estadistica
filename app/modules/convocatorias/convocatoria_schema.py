from datetime import date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.modules.convocatorias.convocatoria_model import EstadoConvocatoria, EstadoTemporal
from app.modules.categorias.categoria_schema import CategoriaDetalleDTO, CategoriaInicioDTO
from app.modules.materiales.material_schema import MaterialesInicioDTO, MaterialesDetalleDTO
from app.core.datetime_utils import UTCDateTimeInput, UTCDateTimeOutput

class ConvocatoriaBaseInput(BaseModel):
    nombre_convocatoria: str
    gestion: int = Field(..., ge=2024)
    descripcion: Optional[str] = None
    inicio_olimpiadas: Optional[date] = None
    fin_olimpiadas: Optional[date] = None
    fecha_inicio_inscripcion: Optional[UTCDateTimeInput] = None
    fecha_fin_inscripcion: Optional[UTCDateTimeInput] = None
    monto_inscripcion: Optional[float] = Field(None, ge=0.0)

class ConvocatoriaCreateDTO(ConvocatoriaBaseInput):
    pass

class ConvocatoriaUpdateDTO(BaseModel):
    nombre_convocatoria: Optional[str] = None
    gestion: Optional[int] = Field(None, ge=2024)
    descripcion: Optional[str] = None
    inicio_olimpiadas: Optional[date] = None
    fin_olimpiadas: Optional[date] = None
    fecha_inicio_inscripcion: Optional[UTCDateTimeInput] = None
    fecha_fin_inscripcion: Optional[UTCDateTimeInput] = None
    monto_inscripcion: Optional[float] = Field(None, ge=0.0)

class ConvocatoriaResponseDTO(BaseModel):
    id_convocatoria: int
    nombre_convocatoria: str
    gestion: int
    descripcion: Optional[str] = None
    inicio_olimpiadas: Optional[date] = None
    fin_olimpiadas: Optional[date] = None
    fecha_inicio_inscripcion: Optional[UTCDateTimeOutput] = None
    fecha_fin_inscripcion: Optional[UTCDateTimeOutput] = None
    monto_inscripcion: Optional[float] = None
    estado: EstadoConvocatoria
    estado_temporal: EstadoTemporal
    fecha_creacion: UTCDateTimeOutput
    fecha_actualizacion: UTCDateTimeOutput

    model_config = ConfigDict(from_attributes=True)

class ConvocatoriaIdDTO(BaseModel):
    id_convocatoria: int

class ConvocatoriaInicioDTO(BaseModel):
    id_convocatoria: int
    nombre_convocatoria: str
    gestion: int
    descripcion: Optional[str] = None
    estado_temporal: str
    monto_inscripcion: Optional[float] = Field(None, ge=0.0)
    inicio_olimpiadas: Optional[date] = None
    fin_olimpiadas: Optional[date] = None
    fecha_inicio_inscripcion: Optional[UTCDateTimeOutput] = None
    fecha_fin_inscripcion: Optional[UTCDateTimeOutput] = None
    categorias: List[CategoriaInicioDTO] = []
    material_principal: MaterialesInicioDTO

class ConvocatoriaDetalleDTO(BaseModel):
    id_convocatoria: int
    nombre_convocatoria: str
    gestion: int
    descripcion: Optional[str] = None
    estado_temporal: str
    monto_inscripcion: Optional[float] = Field(None, ge=0.0)
    inicio_olimpiadas: Optional[date] = None
    fin_olimpiadas: Optional[date] = None
    fecha_inicio_inscripcion: Optional[UTCDateTimeOutput] = None
    fecha_fin_inscripcion: Optional[UTCDateTimeOutput] = None
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

class ConvocatoriaMinified(BaseModel):
    id_convocatoria: int
    nombre_convocatoria: str
    gestion: int

class ConvocatoriaEstadisticasCTO(BaseModel):
    aprobados: int
    pendientes: int
    total: int
    total_categorias: int