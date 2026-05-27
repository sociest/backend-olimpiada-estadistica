from sqlalchemy.orm import Session

from datetime import datetime

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

    def get_activa_o_reciente(self):
        publicadas = self.repository.get_publicadas()
        if not publicadas:
            raise NotFoundError("No hay convocatorias disponibles")

        for convocatoria in publicadas:
            if self.calculate_estado_temporal(convocatoria) == "ACTIVA":
                return convocatoria

        publicadas_ordenadas = sorted(
            publicadas,
            key=lambda item: item.fin_olimpiadas or datetime.min.date(),
            reverse=True,
        )
        return publicadas_ordenadas[0]

    def publish(self, convocatoria_id: int):
        convocatoria = self.get_by_id(convocatoria_id)
        if convocatoria.estado != "BORRADOR":
            raise BusinessRuleError("Solo se puede publicar una convocatoria en borrador")

        convocatoria.estado = "PUBLICADA"

        return self.repository.update(convocatoria)

    def calculate_estado_temporal(self, convocatoria: ConvocatoriaModel):
        ahora = datetime.utcnow()

        if convocatoria.estado == "BORRADOR":
            return "BORRADOR"

        if convocatoria.estado == "CANCELADA":
            return "CANCELADA"

        if convocatoria.fecha_inicio_inscripcion and ahora < convocatoria.fecha_inicio_inscripcion:
            return "PROXIMA"

        if (
            convocatoria.fecha_inicio_inscripcion
            and convocatoria.fecha_fin_inscripcion
            and convocatoria.fecha_inicio_inscripcion <= ahora <= convocatoria.fecha_fin_inscripcion
        ):
            return "INSCRIPCION_EN_CURSO"

        if convocatoria.fin_olimpiadas and ahora.date() <= convocatoria.fin_olimpiadas:
            return "ACTIVA"
        if convocatoria.fin_olimpiadas:
            return "FINALIZADA"

        return "PROXIMA"
