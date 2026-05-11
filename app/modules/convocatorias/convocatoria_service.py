from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.modules.convocatorias.convocatoria_model import ConvocatoriaModel
from app.modules.convocatorias.convocatoria_repository import ConvocatoriaRepository
from app.modules.convocatorias.convocatoria_schema import ConvocatoriaCreateDTO, ConvocatoriaUpdateDTO


class ConvocatoriaService:
    def __init__(self, db: Session):
        self.repository = ConvocatoriaRepository(db)

    def get_by_id(self, convocatoria_id: int):
        convocatoria = self.repository.get_by_id(convocatoria_id)
        if not convocatoria:
            raise NotFoundError("Convocatoria no encontrada")
        return convocatoria

    def get_all(self, page: int, limit: int):
        skip = (page - 1) * limit
        items = self.repository.get_all(skip=skip, limit=limit)
        total = self.repository.count_all()
        return items, total

    def create(self, data: ConvocatoriaCreateDTO):
        convocatoria_data = data.model_dump()
        convocatoria_data["estado"] = "BORRADOR"
        convocatoria = ConvocatoriaModel(**convocatoria_data)
        return self.repository.create(convocatoria)

    def update(self, convocatoria_id: int, data: ConvocatoriaUpdateDTO):
        convocatoria = self.get_by_id(convocatoria_id)

        if convocatoria.estado == "FINALIZADA":
            raise BusinessRuleError("No se puede editar una convocatoria finalizada")

        updates = data.model_dump(exclude_unset=True)
        for key, value in updates.items():
            setattr(convocatoria, key, value)

        if convocatoria.estado != "BORRADOR" and (convocatoria.inicio_olimpiadas is None or convocatoria.fin_olimpiadas is None):
            raise BusinessRuleError("Las fechas de olimpiadas son obligatorias")

        return self.repository.update(convocatoria)

    def delete(self, convocatoria_id: int):
        convocatoria = self.get_by_id(convocatoria_id)
        raise BusinessRuleError("No se puede eliminar una convocatoria")
