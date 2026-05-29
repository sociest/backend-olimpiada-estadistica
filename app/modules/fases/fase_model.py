import enum
from sqlalchemy import CheckConstraint, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class ModalidadFase(str, enum.Enum):
    VIRTUAL = 'VIRTUAL'
    PRESENCIAL = 'PRESENCIAL'
    SEMIPRESENCIAL = 'SEMIPRESENCIAL'


class EstadoEntidad(str, enum.Enum):
    BORRADOR = 'BORRADOR'
    LISTA = 'LISTA'
    ELIMINADA = 'ELIMINADA'


class FaseModel(Base):
    __tablename__ = "fase"

    id_fase = Column(Integer, primary_key=True, index=True)
    id_categoria_fk = Column(Integer, ForeignKey("categoria.id_categoria", ondelete="CASCADE"), nullable=False, index=True)
    nombre_fase = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    modalidad = Column(Enum(ModalidadFase, name="modalidad_fase"), nullable=False)
    estado = Column(Enum(EstadoEntidad, name="estado_entidad"), nullable=False, default=EstadoEntidad.BORRADOR)

    prueba = relationship("FasePruebaModel", back_populates="fase_base", uselist=False, cascade="all, delete")
    preparacion = relationship("FasePreparacionModel", back_populates="fase_base", uselist=False, cascade="all, delete")


class FasePreparacionModel(Base):
    __tablename__ = "fase_preparacion"

    id_fase = Column(Integer, ForeignKey("fase.id_fase", ondelete="CASCADE"), primary_key=True, index=True)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)

    __table_args__ = (
        CheckConstraint('fecha_inicio < fecha_fin', name='check_fechas_preparacion'),
    )

    fase_base = relationship("FaseModel", back_populates="preparacion")


class FasePruebaModel(Base):
    __tablename__ = "fase_prueba"

    id_fase = Column(Integer, ForeignKey("fase.id_fase", ondelete="CASCADE"), primary_key=True, index=True)
    id_fase_anterior = Column(Integer, ForeignKey("fase_prueba.id_fase", ondelete="SET NULL"), nullable=True)
    criterio_aprobacion = Column(Integer, nullable=False)
    fecha_realizacion = Column(DateTime, nullable=False)
    lugar_realizacion = Column(String(255), nullable=True)

    __table_args__ = (
        CheckConstraint('criterio_aprobacion >= 0', name='check_criterio_aprobacion_positivo'),
    )

    fase_base = relationship("FaseModel", back_populates="prueba")
    fase_anterior_rel = relationship("FasePruebaModel", remote_side=[id_fase], back_populates="fase_siguiente_rel")
    fase_siguiente_rel = relationship("FasePruebaModel", back_populates="fase_anterior_rel")