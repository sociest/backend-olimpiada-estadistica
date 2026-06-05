import enum
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.db.database import Base


class TipoModulo(str, enum.Enum):
    CONVOCATORIA = 'CONVOCATORIA'
    INSCRIPCION = 'INSCRIPCION'
    RESULTADO = 'RESULTADO'
    AVISO = 'AVISO'
    ADMINISTRADOR = 'ADMINISTRADOR'
    CONTACTO = 'CONTACTO'
    CAMPANIA = 'CAMPANIA'
    EMAIL_LOG = 'EMAIL_LOG'
    CATEGORIA = 'CATEGORIA'
    FASE_PRUEBA = 'FASE_PRUEBA'
    FASE_PREPARACION = 'FASE_PREPARACION'
    COLABORADOR = 'COLABORADOR'
    ESTUDIANTE = 'ESTUDIANTE'
    DIRECTOR = 'DIRECTOR'
    COLEGIO = 'COLEGIO'
    MATERIAL = 'MATERIAL'
    AUTH = 'AUTH'

class TipoAccion(str, enum.Enum):
    CREAR = 'CREAR'
    ACTUALIZAR = 'ACTUALIZAR'
    ELIMINAR = 'ELIMINAR'
    PUBLICAR = 'PUBLICAR'
    OCULTAR = 'OCULTAR'
    REPROGRAMAR = 'REPROGRAMAR'
    RESPONDER = 'RESPONDER'
    LOGIN_FALLIDO = 'LOGIN_FALLIDO'

class TipoActividad(str, enum.Enum):
    INSCRIPCION = 'INSCRIPCION'
    EMAIL = 'EMAIL'

class AuditoriaModel(Base):
    __tablename__ = "auditoria"

    id_auditoria = Column(Integer, primary_key=True, index=True)
    id_administrador = Column(Integer, ForeignKey("administrador.id_administrador", ondelete="RESTRICT"), nullable=False, index=True)
    accion = Column(Enum(TipoAccion, name="tipo_accion"), nullable=False)
    descripcion = Column(Text, nullable=True)
    modulo = Column(Enum(TipoModulo, name="tipo_modulo"), nullable=True)
    fecha = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)

    administrador = relationship("AdministradorModel")

class ActividadSistemaModel(Base):
    __tablename__ = "actividad_sistema"

    id_actividad = Column(Integer, primary_key=True, index=True)
    tipo = Column(Enum(TipoActividad, name="tipo_actividad"), nullable=False)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha = Column(DateTime(timezone=True), nullable=False, server_default=func.now())