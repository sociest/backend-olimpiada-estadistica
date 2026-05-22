from sqlalchemy.orm import Session

from app.modules.colegios.colegio_model import ColegioModel


class ColegioRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, colegio_id: int):
        return self.db.query(ColegioModel).filter(ColegioModel.id_colegio == colegio_id).first()

    def get_all(self, skip: int, limit: int):
        return self.db.query(ColegioModel).offset(skip).limit(limit).all()

    def count_all(self):
        return self.db.query(ColegioModel).count()

    def create(self, colegio: ColegioModel):
        self.db.add(colegio)
        self.db.commit()
        self.db.refresh(colegio)
        return colegio
    
    def create_no_commit(self, colegio: ColegioModel):
        self.db.add(colegio)
        return colegio

    def update(self, colegio: ColegioModel):
        self.db.commit()
        self.db.refresh(colegio)
        return colegio

    def exists_by_codigo( self, codigo: int):
        return self.db.query(ColegioModel).filter(ColegioModel.codigo == codigo).first() is not None
    
    def commit(self):
        self.db.commit()


    def rollback(self):
        self.db.rollback()
        
    def flush(self):
        self.db.flush()

    def get_all_minified(self):
        return self.db.query(ColegioModel.id_colegio, ColegioModel.nombre, ColegioModel.municipio).all()