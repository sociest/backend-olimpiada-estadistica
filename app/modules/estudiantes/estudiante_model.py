from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base

class EstudianteModel(Base):
    __tablename__ = "estudiante"

    id_estudiante = Column(Integer, ForeignKey("persona.id_persona"), primary_key=True)
    id_colegio = Column(Integer, ForeignKey("colegio.id_colegio"), nullable=False, index=True)
    carnet_identidad = Column(String(50), nullable=False, unique=True)
    curso = Column(Integer, nullable=False)
    nivel = Column(String(20), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    rude = Column(String(50), nullable=True)
    telefono = Column(Integer, nullable=True)
    correo = Column(String(255), nullable=True)

    persona = relationship("PersonaModel", lazy="joined")
    colegio = relationship("ColegioModel", lazy="joined")

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