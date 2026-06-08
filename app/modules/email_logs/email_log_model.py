import enum
from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.db.database import Base

class TipoEmail(str, enum.Enum):
    MASIVO_INSCRIPCION = "MASIVO_INSCRIPCION"
    RESPUESTA_CONTACTO = "RESPUESTA_CONTACTO"
    MAIL_INDIVIDUAL = "MAIL_INDIVIDUAL"
    NOTIFICACION = "NOTIFICACION"

class EstadoEmail(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    EN_PROCESO = "EN_PROCESO"
    ENVIADO = "ENVIADO"
    FALLIDO = "FALLIDO"

class EmailLog(Base):
    __tablename__ = "email_log"

    id_email_log = Column(Integer, primary_key=True, index=True)
    destinatario = Column(String(255), nullable=False)
    asunto = Column(String(255), nullable=False)
    contenido_html = Column(Text, nullable=False)
    tipo = Column(Enum(TipoEmail, name="tipo_email"), nullable=False)
    estado = Column(Enum(EstadoEmail, name="estado_email"), nullable=False, default=EstadoEmail.PENDIENTE)
    error = Column(Text, nullable=True)
    intentos = Column(Integer, nullable=False, default=0)
    ultimo_intento = Column(DateTime(timezone=True), nullable=True)
    fecha_creacion = Column(DateTime(timezone=True), nullable=False, default=func.now())
    fecha_envio = Column(DateTime(timezone=True), nullable=True)
    fecha_actualizacion = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    brevo_message_id = Column(String(255), nullable=True, unique=True)

    id_estudiante = Column(Integer, ForeignKey("estudiante.id_estudiante", ondelete="SET NULL"), nullable=True)
    id_contacto = Column(Integer, ForeignKey("contacto.id_contacto", ondelete="SET NULL"), nullable=True)
    id_campania = Column(Integer, ForeignKey("campania_email.id_campania_email", ondelete="SET NULL"), nullable=True)

    campania = relationship("CampaniaEmail", back_populates="email_logs")
    estudiante = relationship("EstudianteModel", back_populates="email_logs", foreign_keys=[id_estudiante])
    contacto = relationship("ContactoModel", back_populates="email_logs")
