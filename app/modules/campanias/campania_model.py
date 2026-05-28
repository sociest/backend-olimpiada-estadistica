import enum
from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, func, UniqueConstraint
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

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    asunto = Column(String(255), nullable=False)
    estado = Column(Enum(EstadoCampania), nullable=False, default=EstadoCampania.BORRADOR)
    fecha_creacion = Column(DateTime, nullable=False, default=func.now())
    fecha_programada = Column(DateTime, nullable=True)
    fecha_inicio = Column(DateTime, nullable=True)
    fecha_fin = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    destinatarios = relationship("CampaniaDestinatario", back_populates="campania", cascade="all, delete-orphan")
    email_logs = relationship("EmailLog", back_populates="campania")


class CampaniaDestinatario(Base):
    __tablename__ = "campania_destinatario"

    id = Column(Integer, primary_key=True, index=True)
    id_campania = Column(Integer, ForeignKey("campania_email.id", ondelete="CASCADE"), nullable=False)
    id_estudiante = Column(Integer, ForeignKey("estudiante.id_estudiante", ondelete="CASCADE"), nullable=False)
    fecha_creacion = Column(DateTime, nullable=False, default=func.now())

    __table_args__ = (UniqueConstraint('id_campania', 'id_estudiante', name='uq_campania_estudiante'),)

    campania = relationship("CampaniaEmail", back_populates="destinatarios")
    estudiante = relationship("EstudianteModel")