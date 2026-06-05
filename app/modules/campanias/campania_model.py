import enum
from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, func, UniqueConstraint, Text, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.db.database import Base

class EstadoCampania(str, enum.Enum):
    BORRADOR = "BORRADOR"
    PROGRAMADA = "PROGRAMADA"
    EN_PROCESO = "EN_PROCESO"
    FINALIZADA = "FINALIZADA"
    CANCELADA = "CANCELADA"
    FALLIDA = "FALLIDA"

class CampaniaEmail(Base):
    __tablename__ = "campania_email"

    id_campania_email = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    asunto = Column(String(255), nullable=False)
    contenido_mensaje = Column(Text, nullable=False)
    contenido_secundario = Column(Text, nullable=True)
    enlaces = Column(JSONB, nullable=True)
    estado = Column(Enum(EstadoCampania, name="estado_campania"), nullable=False, default=EstadoCampania.BORRADOR)
    fecha_creacion = Column(DateTime(timezone=True), nullable=False, default=func.now())
    fecha_programada = Column(DateTime(timezone=True), nullable=True)
    fecha_inicio = Column(DateTime(timezone=True), nullable=True)
    fecha_fin = Column(DateTime(timezone=True), nullable=True)
    fecha_actualizacion = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())

    destinatarios = relationship("CampaniaDestinatario", back_populates="campania", cascade="all, delete-orphan")
    email_logs = relationship("EmailLog", back_populates="campania")


class CampaniaDestinatario(Base):
    __tablename__ = "campania_destinatario"
    id_campania_email = Column(Integer, ForeignKey("campania_email.id_campania_email", ondelete="CASCADE"), primary_key=True)
    id_estudiante = Column(Integer, ForeignKey("estudiante.id_estudiante", ondelete="CASCADE"), primary_key=True)
    fecha_creacion = Column(DateTime(timezone=True), nullable=False, default=func.now())

    __table_args__ = (UniqueConstraint('id_campania_email', 'id_estudiante', name='uq_campania_estudiante'),)

    campania = relationship("CampaniaEmail", back_populates="destinatarios")
    estudiante = relationship("EstudianteModel")
