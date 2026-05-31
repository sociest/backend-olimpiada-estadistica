from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func, text

from app.db.database import Base


class AdministradorModel(Base):
    __tablename__ = "administrador"

    id_administrador = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    correo = Column(String(255), nullable=False, unique=True, index=True)
    contrasena = Column(String(255), nullable=False)
    estado = Column(String(20), nullable=False, default="ACTIVO", server_default=text("'ACTIVO'"))
