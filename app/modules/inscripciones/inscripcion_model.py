from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship
from app.db.database import Base
class InscripcionModel(Base):
    __tablename__ = "inscripcion"

    id_inscripcion = Column(Integer, primary_key=True, index=True)
    id_estudiante = Column(Integer, ForeignKey("estudiante.id_estudiante"), nullable=False, index=True)
    id_convocatoria = Column(Integer, ForeignKey("convocatoria.id_convocatoria"), nullable=False, index=True)
    id_categoria = Column(Integer, ForeignKey("categoria.id_categoria"), nullable=False, index=True)
    fecha_inscripcion = Column(DateTime, nullable=False, server_default=func.now())
    estado = Column(String(20), nullable=False, server_default="PENDIENTE")

    estudiante = relationship("EstudianteModel", lazy="joined")
    convocatoria = relationship("ConvocatoriaModel", lazy="joined")
    categoria = relationship("CategoriaModel", lazy="joined")
    resultado = relationship("ResultadoModel", lazy="joined")