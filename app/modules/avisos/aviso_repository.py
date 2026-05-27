from datetime import datetime

from sqlalchemy.orm import Session

from app.modules.avisos.aviso_model import AvisoModel


class AvisoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, aviso_id: int):
        return self.db.query(AvisoModel).filter(AvisoModel.id_aviso == aviso_id).first()

    def get_public_by_id(self, aviso_id: int):
        return (
            self.db.query(AvisoModel)
            .filter(AvisoModel.id_aviso == aviso_id)
            .filter(AvisoModel.estado == "PUBLICADO")
            .filter(AvisoModel.fecha_publicacion.isnot(None))
            .filter(AvisoModel.fecha_publicacion <= datetime.now())
            .first()
        )

    def get_all(self, skip: int, limit: int):
        return self.db.query(AvisoModel).offset(skip).limit(limit).all()

    def count_all(self):
        return self.db.query(AvisoModel).count()

    def get_public(self, skip: int, limit: int):
        return (
            self.db.query(AvisoModel)
            .filter(AvisoModel.estado == "PUBLICADO")
            .filter(AvisoModel.fecha_publicacion.isnot(None))
            .filter(AvisoModel.fecha_publicacion <= datetime.now())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_public(self):
        return (
            self.db.query(AvisoModel)
            .filter(AvisoModel.estado == "PUBLICADO")
            .filter(AvisoModel.fecha_publicacion.isnot(None))
            .filter(AvisoModel.fecha_publicacion <= datetime.now())
            .count()
        )

    def get_recent_public(self, limit: int):
        return (
            self.db.query(AvisoModel)
            .filter(AvisoModel.estado == "PUBLICADO")
            .filter(AvisoModel.fecha_publicacion.isnot(None))
            .filter(AvisoModel.fecha_publicacion <= datetime.now())
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
