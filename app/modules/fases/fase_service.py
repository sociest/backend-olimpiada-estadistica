from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.modules.fases.fase_model import EstadoEntidad, FaseModel, FasePreparacionModel, FasePruebaModel
from app.modules.fases.fase_repository import FaseRepository
from app.modules.fases.fase_schema import (
    FaseEstadoUpdateDTO,
    FasePreparacionCreateDTO,
    FasePreparacionUpdateDTO,
    FasePruebaCreateDTO,
    FasePruebaUpdateDTO,
)


class FaseService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = FaseRepository(db)

    def _map_to_polymorphic(self, fase: FaseModel):
        if fase.prueba:
            data = {**fase.__dict__, **fase.prueba.__dict__}
            data["tipo_fase"] = "PRUEBA"
            return data
        elif fase.preparacion:
            data = {**fase.__dict__, **fase.preparacion.__dict__}
            data["tipo_fase"] = "PREPARACION"
            return data
        raise BusinessRuleError("Estado inconsistente: Fase no tiene especialidad asignada.")

    def get_by_id(self, fase_id: int):
        fase = self.repository.get_by_id(fase_id)
        if not fase:
            raise NotFoundError("Fase no encontrada")
        return self._map_to_polymorphic(fase)

    def get_all(self, page: int, limit: int):
        skip = (page - 1) * limit
        items = self.repository.get_all(skip=skip, limit=limit)
        total = self.repository.count_all()
        mapped_items = [self._map_to_polymorphic(item) for item in items]
        return mapped_items, total

    def create_fase_prueba(self, data: FasePruebaCreateDTO):
        if data.id_fase_anterior:
            fase_ant = self.repository.get_by_id(data.id_fase_anterior)
            if not fase_ant or not fase_ant.prueba:
                raise BusinessRuleError("La fase anterior debe existir y ser de tipo PRUEBA.")

        try:
            fase_base = FaseModel(
                id_categoria_fk=data.id_categoria_fk,
                nombre_fase=data.nombre_fase,
                descripcion=data.descripcion,
                modalidad=data.modalidad,
                estado=EstadoEntidad.BORRADOR 
            )
            fase_base = self.repository.create_fase_base(fase_base)

            fase_prueba = FasePruebaModel(
                id_fase=fase_base.id_fase,
                id_fase_anterior=data.id_fase_anterior,
                criterio_aprobacion=data.criterio_aprobacion,
                fecha_realizacion=data.fecha_realizacion,
                lugar_realizacion=data.lugar_realizacion,
            )
            fase_completada = self.repository.create_fase_prueba(fase_prueba)
            return self._map_to_polymorphic(fase_completada)
        except Exception:
            self.db.rollback()
            raise

    def create_fase_preparacion(self, data: FasePreparacionCreateDTO):
        if data.fecha_inicio >= data.fecha_fin:
            raise BusinessRuleError("La fecha de inicio debe ser anterior a la fecha de fin.")
        try:
            fase_base = FaseModel(
                id_categoria_fk=data.id_categoria_fk,
                nombre_fase=data.nombre_fase,
                descripcion=data.descripcion,
                modalidad=data.modalidad,
                estado=EstadoEntidad.BORRADOR 
            )
            fase_base = self.repository.create_fase_base(fase_base)

            fase_preparacion = FasePreparacionModel(
                id_fase=fase_base.id_fase,
                fecha_inicio=data.fecha_inicio,
                fecha_fin=data.fecha_fin,
            )
            fase_completada = self.repository.create_fase_preparacion(fase_preparacion)
            return self._map_to_polymorphic(fase_completada)
        except Exception:
            self.db.rollback()
            raise

    def update_fase_prueba(self, fase_id: int, data: FasePruebaUpdateDTO):
        fase = self.repository.get_by_id(fase_id)
        if not fase or not fase.prueba:
            raise NotFoundError("Fase de Prueba no encontrada")

        if data.id_fase_anterior:
            fase_ant = self.repository.get_by_id(data.id_fase_anterior)
            if not fase_ant or not fase_ant.prueba:
                raise BusinessRuleError("La fase anterior debe existir y ser de tipo PRUEBA.")

        updates = data.model_dump(exclude_unset=True)
        for key, value in updates.items():
            if hasattr(fase, key):
                setattr(fase, key, value)
            elif hasattr(fase.prueba, key):
                setattr(fase.prueba, key, value)

        self.repository.update(fase)
        return self._map_to_polymorphic(fase)

    def update_fase_preparacion(self, fase_id: int, data: FasePreparacionUpdateDTO):
        fase = self.repository.get_by_id(fase_id)
        if not fase or not fase.preparacion:
            raise NotFoundError("Fase de Preparación no encontrada")

        updates = data.model_dump(exclude_unset=True)
        for key, value in updates.items():
            if hasattr(fase, key):
                setattr(fase, key, value)
            elif hasattr(fase.preparacion, key):
                setattr(fase.preparacion, key, value)

        self.repository.update(fase)
        return self._map_to_polymorphic(fase)

    def cambiar_estado(self, fase_id: int, data: FaseEstadoUpdateDTO):
        fase = self.repository.get_by_id(fase_id)
        if not fase:
            raise NotFoundError("Fase no encontrada")

        estado_actual = fase.estado
        nuevo_estado = data.estado

        if estado_actual == EstadoEntidad.BORRADOR and nuevo_estado != EstadoEntidad.LISTA:
            raise BusinessRuleError("De BORRADOR solo se puede pasar a LISTA.")
        if estado_actual == EstadoEntidad.LISTA and nuevo_estado not in [EstadoEntidad.ELIMINADA, EstadoEntidad.BORRADOR]:
            raise BusinessRuleError("De LISTA solo se puede pasar a ELIMINADA o BORRADOR.")
        if estado_actual == EstadoEntidad.ELIMINADA and nuevo_estado != EstadoEntidad.LISTA:
            raise BusinessRuleError("Una fase ELIMINADA solo puede restaurarse a LISTA.")

        fase.estado = nuevo_estado
        self.repository.update(fase)
        return self._map_to_polymorphic(fase)

    def baja_logica(self, fase_id: int):
        dto = FaseEstadoUpdateDTO(estado=EstadoEntidad.ELIMINADA)
        return self.cambiar_estado(fase_id, dto)