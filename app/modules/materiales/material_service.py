from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.core.supabase_storage import SupabaseStorageClient
from app.modules.auth.auth_repository import AuthRepository
from app.modules.materiales.material_model import MaterialModel
from app.modules.materiales.material_repository import MaterialRepository
from app.modules.materiales.material_schema import MaterialCreateDTO, MaterialUpdateDTO


class MaterialService:
    def __init__(self, db: Session):
        self.repository = MaterialRepository(db)
        self.auth_repository = AuthRepository(db)
        self.storage = SupabaseStorageClient()

    def get_public_by_id(self, material_id: int):
        material = self.repository.get_public_by_id(material_id)
        if not material:
            raise NotFoundError("Material no encontrado")
        return material

    def get_by_id(self, material_id: int):
        material = self.repository.get_by_id(material_id)
        if not material:
            raise NotFoundError("Material no encontrado")
        return material

    def get_public(self, page: int, limit: int):
        skip = (page - 1) * limit
        return self.repository.get_public(skip=skip, limit=limit), self.repository.count_public()

    def get_all(self, page: int, limit: int):
        skip = (page - 1) * limit
        return self.repository.get_all(skip=skip, limit=limit), self.repository.count_all()

    async def create(self, data: MaterialCreateDTO, archivo: UploadFile, current_admin_id: int):
        self._validate_relations(data.id_convocatoria, data.id_categoria, data.id_fase)
        content = await archivo.read()
        enlace_acceso = self.storage.upload_material(
            content=content,
            filename=archivo.filename or "material",
            tipo_material=data.tipo_material,
            content_type=archivo.content_type,
        )
        material = MaterialModel(
            nombre_material=data.nombre_material,
            enlace_acceso=enlace_acceso,
            descripcion=data.descripcion,
            tipo_material=data.tipo_material,
            fecha_publicacion=data.fecha_publicacion,
        )
        created_material = self.repository.create(material)
        self.repository.replace_relations(
            material_id=created_material.id_material,
            id_convocatoria=data.id_convocatoria,
            id_categoria=data.id_categoria,
            id_fase=data.id_fase,
        )
        self.auth_repository.create_auditoria(
            admin_id=current_admin_id,
            accion="CREAR_MATERIAL",
            descripcion=f"Material creado: {created_material.nombre_material}",
        )
        return created_material

    async def update(self, material_id: int, data: MaterialUpdateDTO, archivo: UploadFile | None, current_admin_id: int):
        material = self.get_by_id(material_id)
        relation_values = {
            "id_convocatoria": data.id_convocatoria,
            "id_categoria": data.id_categoria,
            "id_fase": data.id_fase,
        }
        has_relation_update = any(value is not None for value in relation_values.values())
        if has_relation_update:
            self._validate_relations(**relation_values)

        updates = data.model_dump(
            exclude_unset=True,
            exclude_none=True,
            exclude={"id_convocatoria", "id_categoria", "id_fase"},
        )
        for key, value in updates.items():
            setattr(material, key, value)

        if archivo is not None:
            content = await archivo.read()
            material.enlace_acceso = self.storage.upload_material(
                content=content,
                filename=archivo.filename or "material",
                tipo_material=material.tipo_material,
                content_type=archivo.content_type,
            )

        updated_material = self.repository.update(material)
        if has_relation_update:
            self.repository.replace_relations(material_id=material_id, **relation_values)

        self.auth_repository.create_auditoria(
            admin_id=current_admin_id,
            accion="ACTUALIZAR_MATERIAL",
            descripcion=f"Material actualizado: {updated_material.nombre_material}",
        )
        return updated_material

    def delete(self, material_id: int, current_admin_id: int):
        material = self.get_by_id(material_id)
        deleted_material = {
            "id_material": material.id_material,
            "nombre_material": material.nombre_material,
            "enlace_acceso": material.enlace_acceso,
            "descripcion": material.descripcion,
            "fecha_creacion": material.fecha_creacion,
            "tipo_material": material.tipo_material,
            "fecha_publicacion": material.fecha_publicacion,
        }
        self.repository.delete(material)
        self.auth_repository.create_auditoria(
            admin_id=current_admin_id,
            accion="ELIMINAR_MATERIAL",
            descripcion=f"Material eliminado: {deleted_material['nombre_material']}",
        )
        return deleted_material

    def _validate_relations(self, id_convocatoria: int | None, id_categoria: int | None, id_fase: int | None):
        if id_convocatoria is not None and not self.repository.convocatoria_exists(id_convocatoria):
            raise BusinessRuleError("La convocatoria no existe")
        if id_categoria is not None and not self.repository.categoria_exists(id_categoria):
            raise BusinessRuleError("La categoria no existe")
        if id_fase is not None and not self.repository.fase_exists(id_fase):
            raise BusinessRuleError("La fase no existe")
