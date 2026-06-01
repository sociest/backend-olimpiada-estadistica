from datetime import datetime
from typing import Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.modules.materiales.material_model import MaterialConvocatoriaModel, MaterialFaseModel, MaterialModel, EstadoMaterial, TipoMaterialEnum
from app.modules.convocatorias.convocatoria_model import ConvocatoriaModel
from sqlalchemy import func

class MaterialRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, material_id: int):
        return self.db.query(MaterialModel).filter(MaterialModel.id_material == material_id).first()

    def get_all(
        self, 
        skip: int, 
        limit: int, 
        estado: Optional[EstadoMaterial], 
        tipo_material: Optional[TipoMaterialEnum],
        fecha_creacion_start: Optional[datetime],
        fecha_creacion_end: Optional[datetime],
        fecha_actualizacion_start: Optional[datetime],
        fecha_actualizacion_end: Optional[datetime],
        fecha_publicacion_start: Optional[datetime],
        fecha_publicacion_end: Optional[datetime],
        busqueda: Optional[str]
    ):
        query = self.db.query(MaterialModel)

        if estado: query = query.filter(MaterialModel.estado == estado)
        if tipo_material: query = query.filter(MaterialModel.tipo_material == tipo_material)
        if fecha_creacion_start: query = query.filter(MaterialModel.fecha_creacion >= fecha_creacion_start)
        if fecha_creacion_end: query = query.filter(MaterialModel.fecha_creacion <= fecha_creacion_end)
        if fecha_actualizacion_start: query = query.filter(MaterialModel.fecha_actualizacion >= fecha_actualizacion_start)
        if fecha_actualizacion_end: query = query.filter(MaterialModel.fecha_actualizacion <= fecha_actualizacion_end)
        if fecha_publicacion_start: query = query.filter(MaterialModel.fecha_publicacion >= fecha_publicacion_start)
        if fecha_publicacion_end: query = query.filter(MaterialModel.fecha_publicacion <= fecha_publicacion_end)
        if busqueda:
            query = query.filter(or_(
                MaterialModel.nombre_material.ilike(f"%{busqueda}%"),
                MaterialModel.descripcion.ilike(f"%{busqueda}%")
            ))

        total = query.count()
        items = query.order_by(MaterialModel.fecha_creacion.desc()).offset(skip).limit(limit).all()
        return items, total

    def get_by_convocatoria(self, id_convocatoria: int):
        return self.db.query(MaterialModel).join(MaterialConvocatoriaModel).filter(MaterialConvocatoriaModel.id_convocatoria == id_convocatoria).all()

    def get_by_fase(self, id_fase: int):
        return self.db.query(MaterialModel).join(MaterialFaseModel).filter(MaterialFaseModel.id_fase == id_fase).all()

    def get_material_principal(self, id_convocatoria: int, tipo: TipoMaterialEnum):
        return self.db.query(MaterialModel).join(MaterialConvocatoriaModel).filter(
            MaterialConvocatoriaModel.id_convocatoria == id_convocatoria,
            MaterialModel.tipo_material == tipo
        ).first()

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

    def link_convocatoria(self, id_material: int, id_convocatoria: int):
        link = MaterialConvocatoriaModel(id_material=id_material, id_convocatoria=id_convocatoria)
        self.db.add(link)
        self.db.commit()

    def unlink_convocatoria(self, id_material: int, id_convocatoria: int):
        self.db.query(MaterialConvocatoriaModel).filter_by(id_material=id_material, id_convocatoria=id_convocatoria).delete()
        self.db.commit()

    def link_fase(self, id_material: int, id_fase: int):
        link = MaterialFaseModel(id_material=id_material, id_fase=id_fase)
        self.db.add(link)
        self.db.commit()

    def unlink_fase(self, id_material: int, id_fase: int):
        self.db.query(MaterialFaseModel).filter_by(id_material=id_material, id_fase=id_fase).delete()
        self.db.commit()

    def check_link_convocatoria(self, id_material: int, id_convocatoria: int) -> bool:
        return self.db.query(MaterialConvocatoriaModel).filter_by(id_material=id_material, id_convocatoria=id_convocatoria).first() is not None

    def check_link_fase(self, id_material: int, id_fase: int) -> bool:
        return self.db.query(MaterialFaseModel).filter_by(id_material=id_material, id_fase=id_fase).first() is not None

    def get_public_materiales(
        self, skip: int, limit: int, tipo_material: Optional[TipoMaterialEnum],
        fecha_start: Optional[datetime], fecha_end: Optional[datetime], busqueda: Optional[str]
    ):
        query = self.db.query(MaterialModel).filter(
            MaterialModel.estado == EstadoMaterial.PUBLICO,
            MaterialModel.fecha_publicacion <= func.now()
        )

        if tipo_material: query = query.filter(MaterialModel.tipo_material == tipo_material)
        if fecha_start: query = query.filter(MaterialModel.fecha_publicacion >= fecha_start)
        if fecha_end: query = query.filter(MaterialModel.fecha_publicacion <= fecha_end)
        if busqueda:
            search = f"%{busqueda}%"
            query = query.filter(or_(
                MaterialModel.nombre_material.ilike(search),
                MaterialModel.descripcion.ilike(search)
            ))

        total = query.count()
        items = query.order_by(MaterialModel.fecha_publicacion.desc()).offset(skip).limit(limit).all()
        return items, total

    def get_public_by_convocatoria(self, id_convocatoria: int):
        return self.db.query(MaterialModel).join(MaterialConvocatoriaModel).filter(
            MaterialConvocatoriaModel.id_convocatoria == id_convocatoria,
            MaterialModel.estado == EstadoMaterial.PUBLICO,
            MaterialModel.fecha_publicacion <= func.now()
        ).order_by(MaterialModel.fecha_publicacion.desc()).all()

    def get_public_by_fase(self, id_fase: int):
        return self.db.query(MaterialModel).join(MaterialFaseModel).filter(
            MaterialFaseModel.id_fase == id_fase,
            MaterialModel.estado == EstadoMaterial.PUBLICO,
            MaterialModel.fecha_publicacion <= func.now()
        ).order_by(MaterialModel.fecha_publicacion.desc()).all()