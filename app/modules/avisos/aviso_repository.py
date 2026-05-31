from datetime import datetime
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.modules.avisos.aviso_model import AvisoModel


class AvisoRepository:
    def __init__(self, db: Session):
        self.db = db

    def _apply_filters(self, query, filters: dict):
        if filters.get("titulo"):
            query = query.filter(AvisoModel.titulo.ilike(f"%{filters['titulo']}%"))
        if filters.get("descripcion"):
            query = query.filter(AvisoModel.descripcion.ilike(f"%{filters['descripcion']}%"))
        if filters.get("tipo"):
            query = query.filter(AvisoModel.tipo == filters["tipo"])
        if filters.get("prioridad"):
            query = query.filter(AvisoModel.prioridad == filters["prioridad"])
        if filters.get("estado"):
            query = query.filter(AvisoModel.estado == filters["estado"])
        if filters.get("fecha_creacion"):
            query = query.filter(func.date(AvisoModel.fecha_creacion) == filters["fecha_creacion"])
        if filters.get("fecha_publicacion"):
            query = query.filter(func.date(AvisoModel.fecha_publicacion) == filters["fecha_publicacion"])
        return query

    def get_by_id(self, aviso_id: int):
        return self.db.query(AvisoModel).filter(AvisoModel.id_aviso == aviso_id).first()

    def get_public_by_id(self, aviso_id: int):
        return (
            self.db.query(AvisoModel)
            .filter(AvisoModel.id_aviso == aviso_id)
            .filter(AvisoModel.estado == "PUBLICADO")
            .filter(AvisoModel.fecha_publicacion.isnot(None))
            .filter(AvisoModel.fecha_publicacion <= datetime.utcnow())
            .first()
        )

    def get_all(self, skip: int, limit: int, filters: dict):
        query = self.db.query(AvisoModel)
        query = self._apply_filters(query, filters)
        return query.order_by(AvisoModel.id_aviso.desc()).offset(skip).limit(limit).all()

    def count_all(self, filters: dict):
        query = self.db.query(AvisoModel)
        query = self._apply_filters(query, filters)
        return query.count()

    def get_public(self, skip: int, limit: int, filters: dict):
        query = self.db.query(AvisoModel)
        query = self._apply_filters(query, filters)
        query = (
            query.filter(AvisoModel.estado == "PUBLICADO")
            .filter(AvisoModel.fecha_publicacion.isnot(None))
            .filter(AvisoModel.fecha_publicacion <= datetime.utcnow())
        )
        return query.order_by(AvisoModel.fecha_publicacion.desc()).offset(skip).limit(limit).all()

    def count_public(self, filters: dict):
        query = self.db.query(AvisoModel)
        query = self._apply_filters(query, filters)
        return (
            query.filter(AvisoModel.estado == "PUBLICADO")
            .filter(AvisoModel.fecha_publicacion.isnot(None))
            .filter(AvisoModel.fecha_publicacion <= datetime.utcnow())
            .count()
        )

    def get_all_public_for_inicio(self):
        prioridad_order = case(
            (AvisoModel.prioridad == 'ALTA', 1),
            (AvisoModel.prioridad == 'MEDIA', 2),
            (AvisoModel.prioridad == 'BAJA', 3),
            else_=4
        )
        return (
            self.db.query(AvisoModel)
            .filter(AvisoModel.estado == "PUBLICADO")
            .filter(AvisoModel.fecha_publicacion.isnot(None))
            .filter(AvisoModel.fecha_publicacion <= datetime.utcnow())
            .order_by(
                func.date(AvisoModel.fecha_publicacion).desc(),
                prioridad_order
            )
            .all()
        )

    def get_recent_public(self, limit: int):
        return (
            self.db.query(AvisoModel)
            .filter(AvisoModel.estado == "PUBLICADO")
            .filter(AvisoModel.fecha_publicacion.isnot(None))
            .filter(AvisoModel.fecha_publicacion <= datetime.utcnow())
            .order_by(AvisoModel.fecha_publicacion.desc())
            .limit(limit)
            .all()
        )

    def create(self, aviso: AvisoModel):
        self.db.add(aviso)
        self.db.commit()
        self.db.refresh(aviso)
        return aviso

    def update(self, aviso: AvisoModel):
        self.db.commit()
        self.db.refresh(aviso)
        return aviso

    def delete(self, aviso: AvisoModel):
        self.db.delete(aviso)
        self.db.commit()
    
    def count_visibles(self) -> int:
        ahora = datetime.now()
        return (
            self.db.query(func.count(AvisoModel.id_aviso))
            .filter(
                AvisoModel.estado == "PUBLICADO",
                AvisoModel.fecha_publicacion <= ahora
            )
            .scalar()
        )    