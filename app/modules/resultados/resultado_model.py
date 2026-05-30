import enum
from sqlalchemy import CheckConstraint, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.database import Base

class EstadoResultado(str, enum.Enum):
    BORRADOR = 'BORRADOR'
    PUBLICADO = 'PUBLICADO'
    OCULTO = 'OCULTO'

class ResultadoModel(Base):
    __tablename__ = "resultado"

    id_resultado = Column(Integer, primary_key=True, index=True)
    id_categoria = Column(Integer, ForeignKey("categoria.id_categoria", ondelete="RESTRICT"), nullable=False)
    id_fase_prueba = Column(Integer, ForeignKey("fase_prueba.id_fase", ondelete="RESTRICT"), nullable=False, index=True)
    id_inscripcion = Column(Integer, ForeignKey("inscripcion.id_inscripcion", ondelete="CASCADE"), nullable=False, index=True)
    nota = Column(Integer, nullable=False)
    observaciones = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, server_default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    estado = Column(Enum(EstadoResultado, name="estado_resultado"), nullable=False, default=EstadoResultado.BORRADOR)

    __table_args__ = (
        CheckConstraint('nota >= 0 AND nota <= 100', name='check_nota_rango'),
    )

    categoria = relationship("CategoriaModel")
    fase_prueba = relationship("FasePruebaModel")
    inscripcion = relationship("InscripcionModel")