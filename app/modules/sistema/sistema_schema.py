from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.core.datetime_utils import UTCDateTimeOutput
from app.modules.sistema.sistema_model import TipoAccion, TipoModulo, TipoActividad


class AuditoriaCreateDTO(BaseModel):
    id_administrador: int
    accion: TipoAccion
    modulo: TipoModulo
    descripcion: Optional[str] = None


class AuditoriaResponseDTO(BaseModel):
    id_auditoria: int
    id_administrador: int
    admin_nombre: str
    accion: str 
    descripcion: Optional[str]
    modulo: TipoModulo
    fecha: UTCDateTimeOutput

    model_config = ConfigDict(from_attributes=True)


class AuditoriaReducidaDTO(BaseModel):
    admin_nombre: str
    modulo: TipoModulo
    accion: str

    model_config = ConfigDict(from_attributes=True)


class ActividadSistemaCreateDTO(BaseModel):
    tipo: TipoActividad
    titulo: str
    descripcion: Optional[str] = None


class ActividadSistemaResponseDTO(BaseModel):
    id_actividad: int
    tipo: TipoActividad
    titulo: str
    descripcion: Optional[str]
    fecha: UTCDateTimeOutput

    model_config = ConfigDict(from_attributes=True)


class DashboardEstadisticasInscripcionDTO(BaseModel):
    total: int
    aprobados: int
    pendientes: int


class DashboardConvocatoriaActivaDTO(BaseModel):
    id_convocatoria: int
    nombre_convocatoria: str


class AdminDashboardResponseDTO(BaseModel):
    convocatoria_activa: Optional[DashboardConvocatoriaActivaDTO]
    inscripciones: DashboardEstadisticasInscripcionDTO
    avisos_visibles: int

class ActividadRecienteDTO(BaseModel):
    id_registro: int
    tipo_registro: str
    fecha: UTCDateTimeOutput
    descripcion: Optional[str] = None
    accion: Optional[str] = None
    modulo: Optional[str] = None
    titulo: Optional[str] = None
    tipo_actividad: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class EventoProximoDTO(BaseModel):
    tipo: str
    titulo: str
    descripcion: str | None = None
    fecha: UTCDateTimeOutput
    referencia_id: int