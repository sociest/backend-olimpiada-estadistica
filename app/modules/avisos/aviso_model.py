from sqlalchemy import Column, DateTime, Integer, String, Text, func

from app.db.database import Base


class AvisoModel(Base):
    __tablename__ = "aviso"

    id_aviso = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=False)
    tipo = Column(String(20), nullable=False)
    fecha_creacion = Column(DateTime, nullable=False, server_default=func.now())
    fecha_publicacion = Column(DateTime, nullable=True)
    estado = Column(String(20), nullable=False, server_default="BORRADOR")
