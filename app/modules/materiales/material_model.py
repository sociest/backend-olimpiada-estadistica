from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text, func

from app.db.database import Base


material_convocatoria = Table(
    "material_convocatoria",
    Base.metadata,
    Column("id_convocatoria", Integer, ForeignKey("convocatoria.id_convocatoria"), primary_key=True),
    Column("id_material", Integer, ForeignKey("material.id_material"), primary_key=True),
    Column("fecha_creacion", DateTime, server_default=func.now()),
)

material_categoria = Table(
    "material_categoria",
    Base.metadata,
    Column("id_categoria", Integer, ForeignKey("categoria.id_categoria"), primary_key=True),
    Column("id_material", Integer, ForeignKey("material.id_material"), primary_key=True),
    Column("fecha_creacion", DateTime, server_default=func.now()),
)

material_fase = Table(
    "material_fase",
    Base.metadata,
    Column("id_fase", Integer, ForeignKey("fase.id_fase"), primary_key=True),
    Column("id_material", Integer, ForeignKey("material.id_material"), primary_key=True),
    Column("fecha_creacion", DateTime, server_default=func.now()),
)


class MaterialModel(Base):
    __tablename__ = "material"

    id_material = Column(Integer, primary_key=True, index=True)
    nombre_material = Column(String(255), nullable=False)
    enlace_acceso = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, nullable=False, server_default=func.now())
    tipo_material = Column(String(30), nullable=False)
    fecha_publicacion = Column(DateTime, nullable=True)
