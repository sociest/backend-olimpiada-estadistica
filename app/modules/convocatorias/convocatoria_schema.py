from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict


class ConvocatoriaBaseDTO(BaseModel):
    nombre_convocatoria: str
    gestion: int
    descripcion: Optional[str] = None
    inicio_olimpiadas: Optional[date] = None
    fin_olimpiadas: Optional[date] = None
    fecha_inicio_inscripcion: Optional[datetime] = None
    fecha_fin_inscripcion: Optional[datetime] = None
    monto_inscripcion: Optional[float] = None
    estado: str


class ConvocatoriaCreateDTO(BaseModel):
    nombre_convocatoria: str
    gestion: int
    descripcion: Optional[str] = None
    inicio_olimpiadas: Optional[date] = None
    fin_olimpiadas: Optional[date] = None
    fecha_inicio_inscripcion: Optional[datetime] = None
    fecha_fin_inscripcion: Optional[datetime] = None
    monto_inscripcion: Optional[float] = None


class ConvocatoriaUpdateDTO(BaseModel):
    nombre_convocatoria: Optional[str] = None
    gestion: Optional[int] = None
    descripcion: Optional[str] = None
    inicio_olimpiadas: Optional[date] = None
    fin_olimpiadas: Optional[date] = None
    fecha_inicio_inscripcion: Optional[datetime] = None
    fecha_fin_inscripcion: Optional[datetime] = None
    monto_inscripcion: Optional[float] = None
    estado: Optional[str] = None


class ConvocatoriaResponseDTO(ConvocatoriaBaseDTO):
    id_convocatoria: int

    model_config = ConfigDict(from_attributes=True)
