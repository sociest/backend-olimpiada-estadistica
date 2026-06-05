import enum
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.db.database import Base


class TipoMaterialEnum(str, enum.Enum):
    EXAMEN = 'EXAMEN'
    SOLUCIONARIO = 'SOLUCIONARIO'
    EJERCICIOS = 'EJERCICIOS'
    DOCUMENTO = 'DOCUMENTO'
    AFICHE = 'AFICHE'
    CONVOCATORIA = 'CONVOCATORIA'
    REGLAMENTO = 'REGLAMENTO'
    DOCUMENTO_EXTERNO = 'DOCUMENTO_EXTERNO'
    ARCHIVO_EXTERNO = 'ARCHIVO_EXTERNO'
    PAGINA_EXTERNA = 'PAGINA_EXTERNA'
    VIDEO_EXTERNO = 'VIDEO_EXTERNO'
    OTRO = 'OTRO'


class EstadoMaterial(str, enum.Enum):
    BORRADOR = 'BORRADOR'
    PUBLICO = 'PUBLICO'
    OCULTO = 'OCULTO'


class EstadoTemporalMaterial(str, enum.Enum):
    BORRADOR = 'BORRADOR'
    OCULTO = 'OCULTO'
    VISIBLE = 'VISIBLE'
    NO_VISIBLE = 'NO_VISIBLE'

class MaterialModel(Base):
    __tablename__ = "material"

    id_material = Column(Integer, primary_key=True, index=True)
    nombre_material = Column(String(255), nullable=False)
    enlace_acceso = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, nullable=False, server_default=func.now())
    fecha_actualizacion = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    estado = Column(Enum(EstadoMaterial, name="estado_material"), nullable=False, default=EstadoMaterial.BORRADOR)
    tipo_material = Column(Enum(TipoMaterialEnum, name="tipo_material_enum"), nullable=False)
    fecha_publicacion = Column(DateTime, nullable=True)

    convocatorias = relationship("MaterialConvocatoriaModel", back_populates="material", cascade="all, delete-orphan")
    fases = relationship("MaterialFaseModel", back_populates="material", cascade="all, delete-orphan")

class MaterialConvocatoriaModel(Base):
    __tablename__ = "material_convocatoria"

    id_convocatoria = Column(Integer, ForeignKey("convocatoria.id_convocatoria", ondelete="CASCADE"), primary_key=True)
    id_material = Column(Integer, ForeignKey("material.id_material", ondelete="CASCADE"), primary_key=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    material = relationship("MaterialModel", back_populates="convocatorias")
    convocatoria = relationship("ConvocatoriaModel")

class MaterialFaseModel(Base):
    __tablename__ = "material_fase"

    id_fase = Column(Integer, ForeignKey("fase.id_fase", ondelete="CASCADE"), primary_key=True)
    id_material = Column(Integer, ForeignKey("material.id_material", ondelete="CASCADE"), primary_key=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    material = relationship("MaterialModel", back_populates="fases")