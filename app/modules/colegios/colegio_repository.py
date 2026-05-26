from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.modules.colegios.colegio_model import ColegioModel
from app.modules.personas.persona_model import PersonaModel
class ColegioRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, colegio_id: int):
        return self.db.query(ColegioModel).filter(ColegioModel.id_colegio == colegio_id).first()

    def get_all(self, skip: int, limit: int):
        return self.db.query(ColegioModel).offset(skip).limit(limit).all()

    def get_all_filtered(self, skip: int, limit: int, filters: dict):
        query = self.db.query(ColegioModel)
        query = self._apply_filters(query, filters)
        return query.offset(skip).limit(limit).all(), query.count()

    def _apply_filters(self, query, filters: dict):
        if filters.get("nombre"):
            query = query.filter(ColegioModel.nombre.ilike(f"%{filters['nombre']}%"))
        if filters.get("municipio"):
            query = query.filter(ColegioModel.municipio.ilike(f"%{filters['municipio']}%"))
        if filters.get("estado"):
            query = query.filter(ColegioModel.estado == filters["estado"])
        if filters.get("tipo"):
            query = query.filter(ColegioModel.tipo == filters["tipo"])
        if filters.get("turno"):
            query = query.filter(ColegioModel.turno == filters["turno"])
        if filters.get("director_nombre"):
            query = query.join(ColegioModel.directores).join(PersonaModel).filter(
                or_(
                    PersonaModel.nombres.ilike(f"%{filters['director_nombre']}%"),
                    PersonaModel.paterno.ilike(f"%{filters['director_nombre']}%")
                )
            )
        return query

    
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

    def update_estado(self, colegio: ColegioModel, estado: str):
        colegio.estado = estado
        self.db.commit()
        self.db.refresh(colegio)
        return colegio

    def delete_physical(self, colegio: ColegioModel):
        self.db.delete(colegio)
        self.db.commit()
    
    def exists_by_codigo( self, codigo: int):
        return self.db.query(ColegioModel).filter(ColegioModel.codigo == codigo).first() is not None
    
    def commit(self):
        self.db.commit()


    def rollback(self):
        self.db.rollback()
        
    def flush(self):
        self.db.flush()

    def get_all_minified(self):
        return self.db.query(ColegioModel.id_colegio, ColegioModel.nombre, ColegioModel.municipio, ColegioModel.turno).all()