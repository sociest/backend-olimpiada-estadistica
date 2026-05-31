import enum
from sqlalchemy import CheckConstraint, Column, Date, DateTime, Enum, Integer, Numeric, String, Text, func
from sqlalchemy.orm import relationship

from app.db.database import Base


class EstadoConvocatoria(str, enum.Enum):
    BORRADOR = 'BORRADOR'
    PUBLICADA = 'PUBLICADA'
    CANCELADA = 'CANCELADA'
    OCULTA = 'OCULTA'


class EstadoTemporal(str, enum.Enum):
    BORRADOR = 'BORRADOR'
    OCULTA = 'OCULTA'
    CANCELADA = 'CANCELADA'
    PROXIMA = 'PROXIMA'
    INSCRIPCIONES_PROXIMAS = 'INSCRIPCIONES PROXIMAS'
    INSCRIPCION_EN_CURSO = 'INSCRIPCION EN CURSO'
    EN_CURSO = 'EN CURSO'
    FINALIZADA = 'FINALIZADA'


class ConvocatoriaModel(Base):
    __tablename__ = "convocatoria"

    id_convocatoria = Column(Integer, primary_key=True, index=True)
    nombre_convocatoria = Column(String(255), nullable=False)
    gestion = Column(Integer, nullable=False)
    descripcion = Column(Text, nullable=True)
    inicio_olimpiadas = Column(Date, nullable=True)
    fin_olimpiadas = Column(Date, nullable=True)
    fecha_inicio_inscripcion = Column(DateTime, nullable=True)
    fecha_fin_inscripcion = Column(DateTime, nullable=True)
    monto_inscripcion = Column(Numeric(10, 2), nullable=True)
    estado = Column(Enum(EstadoConvocatoria, name="estado_convocatoria"), nullable=False, default=EstadoConvocatoria.BORRADOR)
    fecha_creacion = Column(DateTime, nullable=False, server_default=func.now())
    fecha_actualizacion = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint(
            'inicio_olimpiadas IS NULL OR fin_olimpiadas IS NULL OR inicio_olimpiadas <= fin_olimpiadas',
            name='check_fechas_olimpiadas'
        ),
        CheckConstraint(
            'fecha_inicio_inscripcion IS NULL OR fecha_fin_inscripcion IS NULL OR fecha_inicio_inscripcion <= fecha_fin_inscripcion',
            name='check_fechas_inscripcion'
        ),
    )

    categorias = relationship("CategoriaModel", back_populates="convocatoria", cascade="all, delete")