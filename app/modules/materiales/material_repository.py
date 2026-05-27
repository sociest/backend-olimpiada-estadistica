from datetime import datetime

from sqlalchemy import delete, insert, update
from sqlalchemy.orm import Session

from app.modules.categorias.categoria_model import CategoriaModel
from app.modules.convocatorias.convocatoria_model import ConvocatoriaModel
from app.modules.fases.fase_model import FaseModel
from app.modules.materiales.material_model import (
    MaterialModel,
    material_categoria,
    material_convocatoria,
    material_fase,
)


class MaterialRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, material_id: int):
        return self.db.query(MaterialModel).filter(MaterialModel.id_material == material_id).first()

    def get_public_by_id(self, material_id: int):
        return (
            self.db.query(MaterialModel)
            .filter(MaterialModel.id_material == material_id)
            .filter(MaterialModel.estado == "PUBLICADO")
            .filter(MaterialModel.fecha_publicacion.isnot(None))
            .filter(MaterialModel.fecha_publicacion <= datetime.now())
            .first()
        )

    def get_all(self, skip: int, limit: int):
        return self.db.query(MaterialModel).offset(skip).limit(limit).all()

    def count_all(self):
        return self.db.query(MaterialModel).count()

    def get_public(self, skip: int, limit: int):
        return (
            self.db.query(MaterialModel)
            .filter(MaterialModel.estado == "PUBLICADO")
            .filter(MaterialModel.fecha_publicacion.isnot(None))
            .filter(MaterialModel.fecha_publicacion <= datetime.now())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_public(self):
        return (
            self.db.query(MaterialModel)
            .filter(MaterialModel.estado == "PUBLICADO")
            .filter(MaterialModel.fecha_publicacion.isnot(None))
            .filter(MaterialModel.fecha_publicacion <= datetime.now())
            .count()
        )

    def get_public_by_convocatoria(self, convocatoria_id: int, skip: int, limit: int):
        return (
            self.db.query(MaterialModel)
            .join(material_convocatoria, material_convocatoria.c.id_material == MaterialModel.id_material)
            .filter(material_convocatoria.c.id_convocatoria == convocatoria_id)
            .filter(MaterialModel.estado == "PUBLICADO")
            .filter(MaterialModel.fecha_publicacion.isnot(None))
            .filter(MaterialModel.fecha_publicacion <= datetime.now())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_public_by_convocatoria(self, convocatoria_id: int):
        return (
            self.db.query(MaterialModel)
            .join(material_convocatoria, material_convocatoria.c.id_material == MaterialModel.id_material)
            .filter(material_convocatoria.c.id_convocatoria == convocatoria_id)
            .filter(MaterialModel.estado == "PUBLICADO")
            .filter(MaterialModel.fecha_publicacion.isnot(None))
            .filter(MaterialModel.fecha_publicacion <= datetime.now())
            .count()
        )

    def get_public_by_categoria(self, categoria_id: int, skip: int, limit: int):
        return (
            self.db.query(MaterialModel)
            .join(material_categoria, material_categoria.c.id_material == MaterialModel.id_material)
            .filter(material_categoria.c.id_categoria == categoria_id)
            .filter(MaterialModel.estado == "PUBLICADO")
            .filter(MaterialModel.fecha_publicacion.isnot(None))
            .filter(MaterialModel.fecha_publicacion <= datetime.now())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_public_by_categoria(self, categoria_id: int):
        return (
            self.db.query(MaterialModel)
            .join(material_categoria, material_categoria.c.id_material == MaterialModel.id_material)
            .filter(material_categoria.c.id_categoria == categoria_id)
            .filter(MaterialModel.estado == "PUBLICADO")
            .filter(MaterialModel.fecha_publicacion.isnot(None))
            .filter(MaterialModel.fecha_publicacion <= datetime.now())
            .count()
        )

    def get_public_by_fase(self, fase_id: int, skip: int, limit: int):
        return (
            self.db.query(MaterialModel)
            .join(material_fase, material_fase.c.id_material == MaterialModel.id_material)
            .filter(material_fase.c.id_fase == fase_id)
            .filter(MaterialModel.estado == "PUBLICADO")
            .filter(MaterialModel.fecha_publicacion.isnot(None))
            .filter(MaterialModel.fecha_publicacion <= datetime.now())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_public_by_fase(self, fase_id: int):
        return (
            self.db.query(MaterialModel)
            .join(material_fase, material_fase.c.id_material == MaterialModel.id_material)
            .filter(material_fase.c.id_fase == fase_id)
            .filter(MaterialModel.estado == "PUBLICADO")
            .filter(MaterialModel.fecha_publicacion.isnot(None))
            .filter(MaterialModel.fecha_publicacion <= datetime.now())
            .count()
        )

    def get_convocatoria_material_by_tipo_public(self, convocatoria_id: int, importancia_tipo: str):
        return (
            self.db.query(MaterialModel)
            .join(material_convocatoria, material_convocatoria.c.id_material == MaterialModel.id_material)
            .filter(material_convocatoria.c.id_convocatoria == convocatoria_id)
            .filter(material_convocatoria.c.importancia_tipo == importancia_tipo)
            .filter(MaterialModel.estado == "PUBLICADO")
            .filter(MaterialModel.fecha_publicacion.isnot(None))
            .filter(MaterialModel.fecha_publicacion <= datetime.now())
            .first()
        )
    
    def get_principales_public(self, importancia_tipo: str | None = None):
        query = (
            self.db.query(MaterialModel, material_convocatoria.c.importancia_tipo)
            .join(material_convocatoria, material_convocatoria.c.id_material == MaterialModel.id_material)
            .filter(MaterialModel.estado == "PUBLICADO")
            .filter(MaterialModel.fecha_publicacion.isnot(None))
            .filter(MaterialModel.fecha_publicacion <= datetime.now())
        )
        if importancia_tipo:
            query = query.filter(material_convocatoria.c.importancia_tipo == importancia_tipo)
        else:
            query = query.filter(
                material_convocatoria.c.importancia_tipo.in_(["AFICHE", "CONVOCATORIA", "REGLAMENTO"])
            )
        return query.all()

    def create(self, material: MaterialModel):
        self.db.add(material)
        self.db.commit()
        self.db.refresh(material)
        return material

    def update(self, material: MaterialModel):
        self.db.commit()
        self.db.refresh(material)
        return material

    def delete(self, material: MaterialModel):
        self.db.delete(material)
        self.db.commit()

    def convocatoria_exists(self, convocatoria_id: int):
        return self.db.query(ConvocatoriaModel).filter(ConvocatoriaModel.id_convocatoria == convocatoria_id).first() is not None

    def get_convocatoria(self, convocatoria_id: int):
        return (
            self.db.query(ConvocatoriaModel)
            .filter(ConvocatoriaModel.id_convocatoria == convocatoria_id)
            .first()
        )

    def categoria_exists(self, categoria_id: int):
        return self.db.query(CategoriaModel).filter(CategoriaModel.id_categoria == categoria_id).first() is not None

    def fase_exists(self, fase_id: int):
        return self.db.query(FaseModel).filter(FaseModel.id_fase == fase_id).first() is not None

    def replace_relations(
        self,
        material_id: int,
        id_convocatoria: int | None,
        id_categoria: int | None,
        id_fase: int | None,
        importancia_tipo: str = "OTRO",
    ):
        self.db.execute(delete(material_convocatoria).where(material_convocatoria.c.id_material == material_id))
        self.db.execute(delete(material_categoria).where(material_categoria.c.id_material == material_id))
        self.db.execute(delete(material_fase).where(material_fase.c.id_material == material_id))

        if id_convocatoria is not None:
            self.db.execute(
                insert(material_convocatoria).values(
                    id_convocatoria=id_convocatoria,
                    id_material=material_id,
                    importancia_tipo=importancia_tipo,
                )
            )
        if id_categoria is not None:
            self.db.execute(insert(material_categoria).values(id_categoria=id_categoria, id_material=material_id))
        if id_fase is not None:
            self.db.execute(insert(material_fase).values(id_fase=id_fase, id_material=material_id))
        self.db.commit()

    def get_convocatoria_material_by_tipo(self, convocatoria_id: int, importancia_tipo: str):
        return (
            self.db.query(MaterialModel)
            .join(material_convocatoria, material_convocatoria.c.id_material == MaterialModel.id_material)
            .filter(material_convocatoria.c.id_convocatoria == convocatoria_id)
            .filter(material_convocatoria.c.importancia_tipo == importancia_tipo)
            .first()
        )

    def update_importancia_tipo(self, convocatoria_id: int, material_id: int, importancia_tipo: str):
        self.db.execute(
            update(material_convocatoria)
            .where(material_convocatoria.c.id_convocatoria == convocatoria_id)
            .where(material_convocatoria.c.id_material == material_id)
            .values(importancia_tipo=importancia_tipo)
        )
        self.db.commit()

    def set_relacion_convocatoria(self, convocatoria_id: int, material_id: int, importancia_tipo: str):
        self.db.execute(
            delete(material_convocatoria)
            .where(material_convocatoria.c.id_convocatoria == convocatoria_id)
            .where(material_convocatoria.c.id_material == material_id)
        )
        self.db.execute(
            insert(material_convocatoria).values(
                id_convocatoria=convocatoria_id,
                id_material=material_id,
                importancia_tipo=importancia_tipo,
            )
        )
        self.db.commit()
