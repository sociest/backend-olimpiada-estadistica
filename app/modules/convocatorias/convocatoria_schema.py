from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.modules.convocatorias.convocatoria_model import EstadoConvocatoria, EstadoTemporal


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