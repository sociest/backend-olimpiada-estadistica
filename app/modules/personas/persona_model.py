import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.database import Base


class EstadoPersona(str, enum.Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"


class TipoColaborador(str, enum.Enum):
    PERSONAL_ACADEMICO = "PERSONAL ACADEMICO"
    ADMINISTRATIVO = "ADMINISTRATIVO"
    COLABORADOR = "COLABORADOR"


class PersonaModel(Base):
    __tablename__ = "persona"
    id_persona = Column(Integer, primary_key=True, index=True)
    nombres = Column(String(255), nullable=False)
    paterno = Column(String(255), nullable=False)
    materno = Column(String(255), nullable=True)
    estado = Column(Enum(EstadoPersona, name="estado_persona", values_callable=lambda enum: [item.value for item in enum]), nullable=False, default=EstadoPersona.ACTIVO)

class DirectorModel(Base):
    __tablename__ = "director"

    id_director = Column(Integer, ForeignKey("persona.id_persona"), primary_key=True)
    id_colegio = Column(Integer, ForeignKey("colegio.id_colegio"), nullable=True, index=True)
    telefono_1 = Column(String(8), nullable=True)
    telefono_2 = Column(String(8), nullable=True)
    
    colegio = relationship("ColegioModel", back_populates="directores")

    persona = relationship("PersonaModel")

    @property
    def nombres(self):
        return self.persona.nombres if self.persona else "Sin nombre"

    @property
    def paterno(self):
        return self.persona.paterno if self.persona else "Sin apellido"

    @property
    def materno(self):
        return self.persona.materno if self.persona else None

    @property
    def estado(self):
        return self.persona.estado if self.persona else None


class ColaboradorModel(Base):
    __tablename__ = "colaborador"
    id_colaborador = Column(Integer, ForeignKey("persona.id_persona"), primary_key=True)
    perfil = Column(String(255), nullable=True)
    presentacion = Column(Text, nullable=True)
    rol = Column(String(100), nullable=False)
    tipo = Column(Enum(TipoColaborador, name="tipo_colaborador", values_callable=lambda enum: [item.value for item in enum]), nullable=False)
    correo = Column(String(255), nullable=False)

    persona = relationship("PersonaModel")

    @property
    def nombres(self):
        return self.persona.nombres if self.persona else ""

    @property
    def paterno(self):
        return self.persona.paterno if self.persona else ""

    @property
    def materno(self):
        return self.persona.materno if self.persona else ""
