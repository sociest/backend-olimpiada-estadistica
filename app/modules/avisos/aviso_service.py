from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.modules.auth.auth_repository import AuthRepository
from app.modules.avisos.aviso_model import AvisoModel
from app.modules.avisos.aviso_repository import AvisoRepository
from app.modules.avisos.aviso_schema import AvisoCreateDTO, AvisoUpdateDTO


class AvisoService:
    def __init__(self, db: Session):
        self.repository = AvisoRepository(db)
        self.auth_repository = AuthRepository(db)

    def get_public_by_id(self, aviso_id: int):
        aviso = self.repository.get_public_by_id(aviso_id)
        if not aviso:
            raise NotFoundError("Aviso no encontrado")
        return aviso

    def get_by_id(self, aviso_id: int):
        aviso = self.repository.get_by_id(aviso_id)
        if not aviso:
            raise NotFoundError("Aviso no encontrado")
        return aviso

    def get_public(self, page: int, limit: int):
        skip = (page - 1) * limit
        return self.repository.get_public(skip=skip, limit=limit), self.repository.count_public()

    def get_all(self, page: int, limit: int):
        skip = (page - 1) * limit
        return self.repository.get_all(skip=skip, limit=limit), self.repository.count_all()

    def get_recientes(self, limite: int):
        return self.repository.get_recent_public(limite)

    def create(self, data: AvisoCreateDTO, current_admin_id: int):
        aviso = AvisoModel(**data.model_dump())
        aviso.estado = self._resolve_estado(aviso.fecha_publicacion)
        created_aviso = self.repository.create(aviso)
        self.auth_repository.create_auditoria(
            admin_id=current_admin_id,
            accion="CREAR_AVISO",
            descripcion=f"Aviso creado: {created_aviso.titulo}",
        )
        return created_aviso

    def update(self, aviso_id: int, data: AvisoUpdateDTO, current_admin_id: int):
        aviso = self.get_by_id(aviso_id)
        updates = data.model_dump(exclude_unset=True)
        for key, value in updates.items():
            setattr(aviso, key, value)
        if "fecha_publicacion" in updates:
            aviso.estado = self._resolve_estado(aviso.fecha_publicacion)
        updated_aviso = self.repository.update(aviso)
        self.auth_repository.create_auditoria(
            admin_id=current_admin_id,
            accion="ACTUALIZAR_AVISO",
            descripcion=f"Aviso actualizado: {updated_aviso.titulo}",
        )
        return updated_aviso

    def delete(self, aviso_id: int, current_admin_id: int):
        aviso = self.get_by_id(aviso_id)
        deleted = {
            "id_aviso": aviso.id_aviso,
            "titulo": aviso.titulo,
            "descripcion": aviso.descripcion,
            "tipo": aviso.tipo,
            "fecha_creacion": aviso.fecha_creacion,
            "fecha_publicacion": aviso.fecha_publicacion,
        }
        self.repository.delete(aviso)
        self.auth_repository.create_auditoria(
            admin_id=current_admin_id,
            accion="ELIMINAR_AVISO",
            descripcion=f"Aviso eliminado: {deleted['titulo']}",
        )
        return deleted

    def _resolve_estado(self, fecha_publicacion):
        return "PUBLICADO" if fecha_publicacion is not None else "BORRADOR"
