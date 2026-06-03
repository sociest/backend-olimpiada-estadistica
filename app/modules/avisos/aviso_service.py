from datetime import datetime
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.modules.auth.auth_repository import AuthRepository
from app.modules.avisos.aviso_model import AvisoModel, EstadoAviso
from app.modules.avisos.aviso_repository import AvisoRepository
from app.modules.avisos.aviso_schema import AvisoCreateDTO, AvisoUpdateDTO, AvisoEstadoUpdateDTO, AvisoResponseDTO, AvisoPublicoDTO
from app.modules.sistema.sistema_model import AuditoriaModel, TipoAccion, TipoModulo
from app.modules.sistema.sistema_repository import SistemaRepository

class AvisoService:
    def __init__(self, db: Session):
        self.repository = AvisoRepository(db)
        self.auth_repository = AuthRepository(db)
        self.sistema_repository = SistemaRepository(db)

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
        aviso.estado = EstadoAviso.BORRADOR
        created_aviso = self.repository.create(aviso)
        
        auditoria_registro = AuditoriaModel(
            id_administrador=current_admin_id,
            accion=TipoAccion.CREAR,
            modulo=TipoModulo.AVISO,
            descripcion=f"Aviso creado {aviso.titulo} de tipo {aviso.tipo}"
        )
        self.sistema_repository.create_auditoria(auditoria_registro)
        
        return self._with_estado_temporal(created_aviso)

    def update(self, aviso_id: int, data: AvisoUpdateDTO, current_admin_id: int):
        aviso = self._get_model_by_id(aviso_id)
        updates = data.model_dump(exclude_unset=True)
        for key, value in updates.items():
            setattr(aviso, key, value)
          
        updated_aviso = self.repository.update(aviso)
        
        auditoria_registro = AuditoriaModel(
            id_administrador=current_admin_id,
            accion=TipoAccion.ACTUALIZAR,
            modulo=TipoModulo.AVISO,
            descripcion=f"Aviso actualizado {aviso.titulo} de tipo {aviso.tipo}"
        )
        self.sistema_repository.create_auditoria(auditoria_registro)
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
            EstadoAviso.BORRADOR: [EstadoAviso.PUBLICADO],
            EstadoAviso.PUBLICADO: [EstadoAviso.OCULTO],
            EstadoAviso.OCULTO: [EstadoAviso.PUBLICADO],
        }

        if nuevo_estado not in transiciones_validas.get(estado_actual, []):
            raise ValueError(
                f"No se puede cambiar de {estado_actual} a {nuevo_estado}"
            )
        aviso.estado = nuevo_estado
        updated_aviso = self.repository.update(aviso)
        
        auditoria_registro = AuditoriaModel(
            id_administrador=current_admin_id,
            accion=TipoAccion.ACTUALIZAR,
            modulo=TipoModulo.AVISO,
            descripcion=f"Aviso cambio su estado de {estado_actual} a {nuevo_estado} {updated_aviso.titulo} de tipo {updated_aviso.tipo}"
        )
        self.sistema_repository.create_auditoria(auditoria_registro)
        return self._with_estado_temporal(updated_aviso)

    def delete(self, aviso_id: int, current_admin_id: int):
        aviso = self._get_model_by_id(aviso_id)
        deleted = self._with_estado_temporal(aviso)
        descripcion = f"Aviso eliminado {aviso.titulo} de tipo {aviso.tipo}"
        self.repository.delete(aviso)
        
        auditoria_registro = AuditoriaModel(
            id_administrador=current_admin_id,
            accion=TipoAccion.ELIMINAR,
            modulo=TipoModulo.AVISO,
            descripcion=descripcion
        )
        self.sistema_repository.create_auditoria(auditoria_registro)
        
        return deleted

    def _with_estado_temporal(self, aviso: AvisoModel):
        data = AvisoResponseDTO.model_validate(aviso).model_dump()
        data["estado_temporal"] = self._calculate_estado_temporal(aviso)
        return data

    def _calculate_estado_temporal(self, aviso: AvisoModel) -> str:
        if aviso.estado != EstadoAviso.PUBLICADO:
            return "NO_VISIBLE"
        if (
            aviso.fecha_publicacion
            and datetime.now() < aviso.fecha_publicacion
        ):
            return "EN_ESPERA"
        return EstadoAviso.PUBLICADO.value

    def _get_model_by_id(self, aviso_id: int) -> AvisoModel:
        aviso = self.repository.get_by_id(aviso_id)
        if not aviso:
            raise NotFoundError("Aviso no encontrado")
        return aviso

    def get_avisos_publicos_minified(self, page: int, limit: int):
        skip = (page - 1) * limit
        items = self.repository.get_avisos_publicos_minified(skip=skip, limit=limit)
        total = self.repository.count_public(filters={})
        mapped_items = []
        for item in items:
            estado_temporal = self._calculate_estado_temporal(item)
            if (estado_temporal == EstadoAviso.PUBLICADO.value):
                mapped_items.append(AvisoPublicoDTO(
                    prioridad=item.prioridad,
                    titulo = item.titulo,
                    descripcion = item.descripcion,
                    tipo = item.tipo
                ))
        
        return mapped_items, total