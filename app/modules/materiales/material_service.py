from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.core.supabase_storage import SupabaseStorageClient
from app.modules.auth.auth_repository import AuthRepository
from app.modules.materiales.material_model import MaterialModel
from app.modules.materiales.material_repository import MaterialRepository
from datetime import datetime

from app.modules.materiales.material_schema import MaterialCreateDTO, MaterialUpdateDTO


class MaterialService:
    IMPORTANCIA_TIPOS = {"AFICHE", "CONVOCATORIA", "REGLAMENTO"}

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
        return await self._create_material(data, archivo, current_admin_id, allow_principal=False)

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

        if "nombre_material" in updates:
            material.nombre_material = self._normalize_nombre(material.nombre_material)
        if "descripcion" in updates:
            material.descripcion = self._normalize_descripcion(material.descripcion)
        if "fecha_publicacion" in updates:
            material.visibilidad = self._resolve_visibilidad(material.fecha_publicacion)
        if "tipo_material" in updates and material.tipo_material == "PRINCIPAL":
            raise BusinessRuleError("Tipo de material no permitido en este endpoint")

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

    async def create_material_convocatoria(self, convocatoria_id: int, data: MaterialCreateDTO, archivo: UploadFile, current_admin_id: int):
        self._validate_relations(convocatoria_id, None, None)
        data = MaterialCreateDTO(
            nombre_material=data.nombre_material,
            descripcion=data.descripcion,
            tipo_material=data.tipo_material,
            fecha_publicacion=data.fecha_publicacion,
            id_convocatoria=convocatoria_id,
        )
        return await self._create_material(data, archivo, current_admin_id, allow_principal=False)

    async def create_material_categoria(self, categoria_id: int, data: MaterialCreateDTO, archivo: UploadFile, current_admin_id: int):
        self._validate_relations(None, categoria_id, None)
        data = MaterialCreateDTO(
            nombre_material=data.nombre_material,
            descripcion=data.descripcion,
            tipo_material=data.tipo_material,
            fecha_publicacion=data.fecha_publicacion,
            id_categoria=categoria_id,
        )
        return await self._create_material(data, archivo, current_admin_id, allow_principal=False)

    async def create_material_fase(self, fase_id: int, data: MaterialCreateDTO, archivo: UploadFile, current_admin_id: int):
        self._validate_relations(None, None, fase_id)
        data = MaterialCreateDTO(
            nombre_material=data.nombre_material,
            descripcion=data.descripcion,
            tipo_material=data.tipo_material,
            fecha_publicacion=data.fecha_publicacion,
            id_fase=fase_id,
        )
        return await self._create_material(data, archivo, current_admin_id, allow_principal=False)

    async def create_material_principal(
        self,
        convocatoria_id: int,
        importancia_tipo: str,
        data: MaterialCreateDTO,
        archivo: UploadFile,
        current_admin_id: int,
    ):
        if importancia_tipo not in self.IMPORTANCIA_TIPOS:
            raise BusinessRuleError("Tipo principal no permitido")
        convocatoria = self.repository.get_convocatoria(convocatoria_id)
        if not convocatoria:
            raise BusinessRuleError("La convocatoria no existe")
        existing = self.repository.get_convocatoria_material_by_tipo(convocatoria_id, importancia_tipo)
        data = MaterialCreateDTO(
            nombre_material=f"{convocatoria.gestion}_{importancia_tipo}_{convocatoria_id}",
            descripcion=None,
            tipo_material="PRINCIPAL",
            fecha_publicacion=datetime.now(),
            id_convocatoria=convocatoria_id,
        )
        material = await self._create_material(data, archivo, current_admin_id, allow_principal=True)
        if existing is not None:
            existing.visibilidad = "PRIVADO"
            existing.tipo_material = "OTRO"
            self.repository.update(existing)
            self.repository.update_importancia_tipo(convocatoria_id, existing.id_material, "OTRO")
        self.repository.update_importancia_tipo(convocatoria_id, material.id_material, importancia_tipo)
        return material

    def asignar_material_principal(self, convocatoria_id: int, material_id: int, importancia_tipo: str, current_admin_id: int):
        if importancia_tipo not in self.IMPORTANCIA_TIPOS:
            raise BusinessRuleError("Tipo principal no permitido")

        convocatoria = self.repository.get_convocatoria(convocatoria_id)
        if not convocatoria:
            raise BusinessRuleError("La convocatoria no existe")

        material = self.get_by_id(material_id)
        if material.tipo_material != "PRINCIPAL":
            raise BusinessRuleError("Tipo de material no coincide con el tipo principal")

        existing = self.repository.get_convocatoria_material_by_tipo(convocatoria_id, importancia_tipo)
        if existing is not None:
            existing.visibilidad = "PRIVADO"
            existing.tipo_material = "OTRO"
            self.repository.update(existing)
            self.repository.update_importancia_tipo(convocatoria_id, existing.id_material, "OTRO")

        material.nombre_material = f"{convocatoria.gestion}_{importancia_tipo}_{convocatoria_id}"
        material.descripcion = None
        material.fecha_publicacion = datetime.now()
        material.visibilidad = "PUBLICO"
        self.repository.update(material)
        self.repository.set_relacion_convocatoria(convocatoria_id, material_id, importancia_tipo)

        self.auth_repository.create_auditoria(
            admin_id=current_admin_id,
            accion="ASIGNAR_MATERIAL_PRINCIPAL",
            descripcion=f"Material principal asignado: {material.nombre_material}",
        )
        return material

    def get_material_principal(self, convocatoria_id: int, importancia_tipo: str):
        material = self.repository.get_convocatoria_material_by_tipo(convocatoria_id, importancia_tipo)
        if not material:
            raise NotFoundError("Material no encontrado")
        return material

    def get_all_material_principal(self, convocatoria_id: int):
        return self.repository.get_all_material_principal(convocatoria_id)

    def delete_material_principal(self, convocatoria_id: int, importancia_tipo: str, current_admin_id: int):
        material = self.get_material_principal(convocatoria_id, importancia_tipo)
        material.visibilidad = "PRIVADO"
        material.tipo_material = "OTRO"
        self.repository.update(material)
        self.repository.update_importancia_tipo(convocatoria_id, material.id_material, "OTRO")
        self.auth_repository.create_auditoria(
            admin_id=current_admin_id,
            accion="ELIMINAR_MATERIAL_PRINCIPAL",
            descripcion=f"Material principal eliminado: {material.nombre_material}",
        )
        return material

    def _normalize_nombre(self, nombre: str) -> str:
        return nombre.strip().upper()

    def _normalize_descripcion(self, descripcion: str | None) -> str | None:
        if descripcion is None:
            return None
        cleaned = descripcion.strip()
        if not cleaned:
            return cleaned
        return f"{cleaned[0].upper()}{cleaned[1:]}"

    def _resolve_visibilidad(self, fecha_publicacion):
        return "PUBLICO" if fecha_publicacion is not None else "PRIVADO"

    def get_material_principal_public(self, convocatoria_id: int, importancia_tipo: str):
        material = self.repository.get_convocatoria_material_by_tipo_public(convocatoria_id, importancia_tipo)
        if not material:
            raise NotFoundError("Material no encontrado")
        return material

    def get_public_by_convocatoria(self, convocatoria_id: int, page: int, limit: int):
        skip = (page - 1) * limit
        items = self.repository.get_public_by_convocatoria(convocatoria_id, skip=skip, limit=limit)
        total = self.repository.count_public_by_convocatoria(convocatoria_id)
        return items, total

    def get_public_by_categoria(self, categoria_id: int, page: int, limit: int):
        skip = (page - 1) * limit
        items = self.repository.get_public_by_categoria(categoria_id, skip=skip, limit=limit)
        total = self.repository.count_public_by_categoria(categoria_id)
        return items, total

    def get_public_by_fase(self, fase_id: int, page: int, limit: int):
        skip = (page - 1) * limit
        items = self.repository.get_public_by_fase(fase_id, skip=skip, limit=limit)
        total = self.repository.count_public_by_fase(fase_id)
        return items, total

    def get_principales_public(self, importancia_tipo: str | None = None):
        if importancia_tipo and importancia_tipo not in self.IMPORTANCIA_TIPOS:
            raise BusinessRuleError("Tipo de importancia no valido")
        return self.repository.get_principales_public(importancia_tipo)

    async def _create_material(
        self,
        data: MaterialCreateDTO,
        archivo: UploadFile,
        current_admin_id: int,
        allow_principal: bool,
    ):
        if not allow_principal and data.tipo_material == "PRINCIPAL":
            raise BusinessRuleError("Tipo de material no permitido en este endpoint")

        self._validate_relations(data.id_convocatoria, data.id_categoria, data.id_fase)
        content = await archivo.read()
        enlace_acceso = self.storage.upload_material(
            content=content,
            filename=archivo.filename or "material",
            tipo_material=data.tipo_material,
            content_type=archivo.content_type,
        )
        nombre_material = self._normalize_nombre(data.nombre_material)
        descripcion = self._normalize_descripcion(data.descripcion)
        visibilidad = self._resolve_visibilidad(data.fecha_publicacion)

        material = MaterialModel(
            nombre_material=nombre_material,
            enlace_acceso=enlace_acceso,
            descripcion=descripcion,
            visibilidad=visibilidad,
            tipo_material=data.tipo_material,
            fecha_publicacion=data.fecha_publicacion,
        )
        created_material = self.repository.create(material)
        self.repository.replace_relations(
            material_id=created_material.id_material,
            id_convocatoria=data.id_convocatoria,
            id_categoria=data.id_categoria,
            id_fase=data.id_fase,
            importancia_tipo="OTRO",
        )
        self.auth_repository.create_auditoria(
            admin_id=current_admin_id,
            accion="CREAR_MATERIAL",
            descripcion=f"Material creado: {created_material.nombre_material}",
        )
        return created_material
