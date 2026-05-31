from datetime import datetime
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.modules.auth.auth_repository import AuthRepository
from app.modules.avisos.aviso_model import AvisoModel
from app.modules.avisos.aviso_repository import AvisoRepository
from app.modules.avisos.aviso_schema import AvisoCreateDTO, AvisoUpdateDTO, AvisoEstadoUpdateDTO, AvisoResponseDTO


class AvisoService:
    def __init__(self, db: Session):
        self.repository = AvisoRepository(db)
        self.auth_repository = AuthRepository(db)

    def get_public_by_id(self, aviso_id: int):
        aviso = self.repository.get_public_by_id(aviso_id)
        if not aviso:
            raise NotFoundError("Aviso no encontrado o no está disponible públicamente")
        return self._with_estado_temporal(aviso)

    def get_by_id(self, aviso_id: int):
        aviso = self._get_model_by_id(aviso_id)
        return self._with_estado_temporal(aviso)

    def get_public(self, page: int, limit: int, filters: dict):
        skip = (page - 1) * limit
        items = [self._with_estado_temporal(item) for item in self.repository.get_public(skip=skip, limit=limit, filters=filters)]
        total = self.repository.count_public(filters=filters)
        return items, total

    def get_all(self, page: int, limit: int, filters: dict):
        skip = (page - 1) * limit
        items = [self._with_estado_temporal(item) for item in self.repository.get_all(skip=skip, limit=limit, filters=filters)]
        total = self.repository.count_all(filters=filters)
        return items, total

    def get_recientes(self, limite: int):
        return [self._with_estado_temporal(item) for item in self.repository.get_recent_public(limite)]

    def get_avisos_inicio(self):
        items = self.repository.get_all_public_for_inicio()
        return [self._with_estado_temporal(item) for item in items]

    def create(self, data: AvisoCreateDTO, current_admin_id: int):
        aviso = AvisoModel(**data.model_dump())
        aviso.estado = "BORRADOR"
        created_aviso = self.repository.create(aviso)
        return self._with_estado_temporal(created_aviso)

    def update(self, aviso_id: int, data: AvisoUpdateDTO, current_admin_id: int):
        aviso = self._get_model_by_id(aviso_id)
        updates = data.model_dump(exclude_unset=True)
        for key, value in updates.items():
            setattr(aviso, key, value)
          
        updated_aviso = self.repository.update(aviso)
        return self._with_estado_temporal(updated_aviso)

    def cambiar_estado(
        self,
        aviso_id: int,
        data: AvisoEstadoUpdateDTO,
        current_admin_id: int
    ):
        aviso = self._get_model_by_id(aviso_id)
        estado_actual = aviso.estado
        nuevo_estado = data.estado
        transiciones_validas = {
            "BORRADOR": ["PUBLICADO"],
            "PUBLICADO": ["OCULTO"],
            "OCULTO": ["PUBLICADO"],
        }

        if nuevo_estado not in transiciones_validas.get(estado_actual, []):
            raise ValueError(
                f"No se puede cambiar de {estado_actual} a {nuevo_estado}"
            )
        aviso.estado = nuevo_estado
        updated_aviso = self.repository.update(aviso)
        return self._with_estado_temporal(updated_aviso)

    def delete(self, aviso_id: int, current_admin_id: int):
        aviso = self._get_model_by_id(aviso_id)
        deleted = self._with_estado_temporal(aviso)
        self.repository.delete(aviso)
        return deleted

    def _with_estado_temporal(self, aviso: AvisoModel):
        data = AvisoResponseDTO.model_validate(aviso).model_dump()
        data["estado_temporal"] = self._calculate_estado_temporal(aviso)
        return data

    def _calculate_estado_temporal(self, aviso: AvisoModel) -> str:
        if aviso.estado != "PUBLICADO":
            return "NO_VISIBLE"
        if (
            aviso.fecha_publicacion
            and datetime.utcnow() < aviso.fecha_publicacion
        ):
            return "EN_ESPERA"
        return "PUBLICADO"

    def _get_model_by_id(self, aviso_id: int) -> AvisoModel:
        aviso = self.repository.get_by_id(aviso_id)
        if not aviso:
            raise NotFoundError("Aviso no encontrado")
        return aviso