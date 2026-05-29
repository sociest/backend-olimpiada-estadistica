import enum
from sqlalchemy import Column, DateTime, Integer, String, Text, func, Enum
from sqlalchemy.orm import relationship

from app.db.database import Base

class EstadoContacto(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    RESPONDIDO = "RESPONDIDO"
    LEIDO = "LEIDO"

class ContactoModel(Base):
    __tablename__ = "contacto"

    id_contacto = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String(100), nullable=False)
    correo_electronico = Column(String(150), nullable=False, index=True)
    asunto = Column(String(200), nullable=False)
    mensaje = Column(Text, nullable=False)
    creado_en = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    cambio_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    estado = Column(Enum(EstadoContacto), nullable=False, default=EstadoContacto.PENDIENTE)

    email_logs = relationship("EmailLog", back_populates="contacto", cascade="all, delete-orphan", foreign_keys="[EmailLog.id_contacto]")