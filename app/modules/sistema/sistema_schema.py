from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

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
    fecha: datetime

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
    fecha: datetime

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