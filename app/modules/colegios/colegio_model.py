import enum

from sqlalchemy import Column, Enum, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base


class TipoColegio(str, enum.Enum):
    PRIVADO = "PRIVADO"
    CONVENIO = "CONVENIO"
    PUBLICO = "PUBLICO"


class TurnoColegio(str, enum.Enum):
    MANANA = "MAÑANA"
    TARDE = "TARDE"
    NOCHE = "NOCHE"
    MIXTO = "MIXTO"


class EstadoColegio(str, enum.Enum):
    REVISADO = "REVISADO"
    RECHAZADO = "RECHAZADO"
    PENDIENTE = "PENDIENTE"
    INACTIVO = "INACTIVO"


class ColegioModel(Base):
    __tablename__ = "colegio"

    id_colegio = Column(Integer, primary_key=True, index=True)
    codigo = Column(Integer, nullable=False, unique=True)
    nombre = Column(String(255), nullable=False)
    tipo = Column(Enum(TipoColegio, name="tipo_colegio", values_callable=lambda enum: [item.value for item in enum]), nullable=False)
    turno = Column(Enum(TurnoColegio, name="turno_colegio", values_callable=lambda enum: [item.value for item in enum]), nullable=False)
    departamento = Column(String(100), nullable=False)
    municipio = Column(String(100), nullable=False)
    calle = Column(String(255), nullable=True)
    estado = Column(Enum(EstadoColegio, name="estado_colegio", values_callable=lambda enum: [item.value for item in enum]), nullable=False, default=EstadoColegio.PENDIENTE)
    directores = relationship("DirectorModel", back_populates="colegio")
