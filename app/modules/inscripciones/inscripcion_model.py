import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import relationship
from app.db.database import Base


class EstadoInscripcion(str, enum.Enum):
    RECHAZADO = "RECHAZADO"
    PENDIENTE = "PENDIENTE"
    APROBADO = "APROBADO"


class InscripcionModel(Base):
    __tablename__ = "inscripcion"

    id_inscripcion = Column(Integer, primary_key=True, index=True)
    id_estudiante = Column(Integer, ForeignKey("estudiante.id_estudiante", ondelete="RESTRICT"), nullable=False, index=True)
    id_convocatoria = Column(Integer, ForeignKey("convocatoria.id_convocatoria", ondelete="RESTRICT"), nullable=False, index=True)
    id_categoria = Column(Integer, ForeignKey("categoria.id_categoria", ondelete="RESTRICT"), nullable=False, index=True)
    fecha_inscripcion = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    estado = Column(Enum(EstadoInscripcion, name="estado_inscripcion"), nullable=False, default=EstadoInscripcion.PENDIENTE)

    estudiante = relationship("EstudianteModel", lazy="joined")
    convocatoria = relationship("ConvocatoriaModel", lazy="joined")
    categoria = relationship("CategoriaModel", lazy="joined")
    resultado = relationship("ResultadoModel", lazy="joined", back_populates="inscripcion")

    __table_args__ = (
        UniqueConstraint("id_estudiante", "id_convocatoria", name="uq_inscripcion_estudiante_convocatoria"),
    )
