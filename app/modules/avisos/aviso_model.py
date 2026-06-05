import enum

from sqlalchemy import Column, DateTime, Enum, Integer, String, Text, func
from app.db.database import Base


class TipoAviso(str, enum.Enum):
    CONVOCATORIA = "CONVOCATORIA"
    INSCRIPCION = "INSCRIPCION"
    CRONOGRAMA = "CRONOGRAMA"
    MATERIAL = "MATERIAL"
    EXAMEN = "EXAMEN"
    LOGISTICA = "LOGISTICA"
    RESULTADO = "RESULTADO"
    RECLAMO = "RECLAMO"
    CEREMONIA = "CEREMONIA"
    CAPACITACION = "CAPACITACION"
    MANTENIMIENTO = "MANTENIMIENTO"
    SOPORTE = "SOPORTE"
    GENERAL = "GENERAL"


class EstadoAviso(str, enum.Enum):
    BORRADOR = "BORRADOR"
    PUBLICADO = "PUBLICADO"
    OCULTO = "OCULTO"


class AvisoPrioridad(str, enum.Enum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"


class AvisoModel(Base):
    __tablename__ = "aviso"

    id_aviso = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=False)
    tipo = Column(Enum(TipoAviso, name="tipo_aviso"), nullable=False, default=TipoAviso.GENERAL)
    prioridad = Column(Enum(AvisoPrioridad, name="aviso_prioridad"), nullable=False, default=AvisoPrioridad.MEDIA)
    fecha_creacion = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    fecha_publicacion = Column(DateTime(timezone=True), nullable=True)
    estado = Column(Enum(EstadoAviso, name="estado_aviso"), nullable=False, default=EstadoAviso.BORRADOR)
