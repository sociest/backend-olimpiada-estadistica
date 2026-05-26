from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base


class ColegioModel(Base):
    __tablename__ = "colegio"

    id_colegio = Column(Integer, primary_key=True, index=True)
    codigo = Column(Integer, nullable=False, unique=True)
    nombre = Column(String(255), nullable=False)
    tipo = Column(String(20), nullable=False)
    turno = Column(String(20), nullable=False)
    departamento = Column(String(100), nullable=False)
    municipio = Column(String(100), nullable=False)
    calle = Column(String(255), nullable=True)
    estado = Column(String(20), nullable=False, default="PENDIENTE")
    directores = relationship("DirectorModel", back_populates="colegio")
