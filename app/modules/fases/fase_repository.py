from sqlalchemy.orm import Session, joinedload
from app.modules.fases.fase_model import EstadoEntidad, FaseModel, FasePreparacionModel, FasePruebaModel

class FaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_base_query(self):
        return self.db.query(FaseModel).options(
            joinedload(FaseModel.prueba),
            joinedload(FaseModel.preparacion)
        )

    def get_all(self, skip: int, limit: int):
        return self.get_base_query().offset(skip).limit(limit).all()

    def count_all(self):
        return self.db.query(FaseModel).count()

    def get_by_id(self, fase_id: int):
        return self.get_base_query().filter(FaseModel.id_fase == fase_id).first()
    
    def get_by_id_categoria(self, categoria_id: int):
        return self.get_base_query().filter(FaseModel.id_categoria_fk == categoria_id).all()

    def get_activos_by_categoria(self, categoria_id: int, skip: int, limit: int):
        return (
            self.get_base_query()
            .filter(FaseModel.id_categoria_fk == categoria_id, FaseModel.estado != EstadoEntidad.ELIMINADA)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_activos_by_categoria(self, categoria_id: int):
        return self.db.query(FaseModel).filter(
            FaseModel.id_categoria_fk == categoria_id, FaseModel.estado != EstadoEntidad.ELIMINADA
        ).count()

    def create_fase_base(self, fase: FaseModel) -> FaseModel:
        self.db.add(fase)
        self.db.flush()
        return fase

    def create_fase_prueba(self, fase_prueba: FasePruebaModel):
        self.db.add(fase_prueba)
        self.db.commit()
        self.db.refresh(fase_prueba.fase_base)
        return fase_prueba.fase_base

    def create_fase_preparacion(self, fase_preparacion: FasePreparacionModel):
        self.db.add(fase_preparacion)
        self.db.commit()
        self.db.refresh(fase_preparacion.fase_base)
        return fase_preparacion.fase_base

    def update(self, entidad_model):
        self.db.commit()
        self.db.refresh(entidad_model)
        return entidad_model
    
    def delete(self, entidad_model):
        self.db.delete(entidad_model)
        self.db.commit()
        