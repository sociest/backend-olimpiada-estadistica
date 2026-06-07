import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.core.supabase_storage import SupabaseStorageClient
from app.modules.materiales.material_model import MaterialModel, EstadoMaterial, EstadoTemporalMaterial, TipoMaterialEnum
from app.modules.materiales.material_repository import MaterialRepository
from app.modules.materiales.material_schema import MaterialExternoCreateDTO, MaterialUpdateDTO, LinkMaterialPrincipalResponse, LinkMaterialPrincipalDTO
from app.modules.convocatorias.convocatoria_repository import ConvocatoriaRepository
from app.modules.convocatorias.convocatoria_model import EstadoConvocatoria
from app.modules.sistema.sistema_model import AuditoriaModel, TipoAccion, TipoModulo
from app.modules.sistema.sistema_repository import SistemaRepository


TIPOS_EXTERNOS = {TipoMaterialEnum.DOCUMENTO_EXTERNO, TipoMaterialEnum.PAGINA_EXTERNA, TipoMaterialEnum.VIDEO_EXTERNO, TipoMaterialEnum.ARCHIVO_EXTERNO, TipoMaterialEnum}
TIPOS_PRINCIPALES = {TipoMaterialEnum.AFICHE, TipoMaterialEnum.CONVOCATORIA, TipoMaterialEnum.REGLAMENTO}

class MaterialService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = MaterialRepository(db)
        self.convocatoria_repo = ConvocatoriaRepository(db)
        self.sistema_repository = SistemaRepository(db)
        self.storage = SupabaseStorageClient()

    def calcular_estado_temporal(self, material: MaterialModel) -> EstadoTemporalMaterial:
        ahora = datetime.now(timezone.utc)
        if material.estado in [EstadoMaterial.BORRADOR, EstadoMaterial.OCULTO]:
            return EstadoTemporalMaterial(material.estado.value)
        if material.fecha_publicacion and ahora >= material.fecha_publicacion:
            return EstadoTemporalMaterial.VISIBLE
        return EstadoTemporalMaterial.NO_VISIBLE

    def _map_response(self, material: MaterialModel) -> dict:
        data = {}
        for column in material.__table__.columns:
            value = getattr(material, column.name)
            # Si el valor es un Enum, convertirlo a su valor primitivo
            if hasattr(value, 'value'):
                value = value.value
            data[column.name] = value
        estado_temp = self.calcular_estado_temporal(material)
        data["estado_temporal"] = estado_temp.value if hasattr(estado_temp, 'value') else estado_temp
        return data
    
    def _map_detalle_response(self, material: MaterialModel):
        data = self._map_response(material)
        data["convocatorias"] = [
            {"id_convocatoria": rel.convocatoria.id_convocatoria, "nombre_convocatoria": rel.convocatoria.nombre_convocatoria, "gestion": rel.convocatoria.gestion}
            for rel in material.convocatorias
        ]
        data["fases"] = [
            {"id_fase": rel.fase.id_fase, "nombre_fase": rel.fase.nombre_fase, "nombre_categoria": rel.fase.categoria.nombre_categoria}
            for rel in material.fases if hasattr(rel, 'fase')
        ]
        return data

    def _generar_nombre_supabase(self, nombre_material: str, extension: str, fecha: datetime) -> str:
        nombre_limpio = nombre_material.replace(" ", "_")
        fecha_str = fecha.strftime("%Y%m%d%H%M%S")
        return f"{nombre_limpio}_{fecha_str}{extension}"

    def get_all(self, skip, limit, estado, tipo_material, fc_start, fc_end, fa_start, fa_end, fp_start, fp_end, busqueda):
        items, total = self.repository.get_all(skip, limit, estado, tipo_material, fc_start, fc_end, fa_start, fa_end, fp_start, fp_end, busqueda)
        return [self._map_response(i) for i in items], total

    def get_by_id(self, material_id: int):
        material = self.repository.get_by_id(material_id)
        if not material: raise NotFoundError("Material no encontrado")
        return self._map_detalle_response(material)

    def get_by_convocatoria(self, id_convocatoria: int):
        return [self._map_response(i) for i in self.repository.get_by_convocatoria(id_convocatoria)]

    def get_by_fase(self, id_fase: int):
        return [self._map_response(i) for i in self.repository.get_by_fase(id_fase)]

    def create_externo(self, data: MaterialExternoCreateDTO, current_admin_id: int):
        if data.fecha_publicacion is None:
            raise BusinessRuleError("La fecha de publicación es requerida")
        if data.tipo_material not in TIPOS_EXTERNOS:
            raise BusinessRuleError("Tipo de material no es externo")
        if data.fecha_publicacion and data.fecha_publicacion < datetime.now(timezone.utc):
            raise BusinessRuleError("La fecha de publicación debe ser igual o posterior a la actual")

        material = MaterialModel(
            nombre_material=data.nombre_material.upper(),
            descripcion=data.descripcion,
            tipo_material=data.tipo_material,
            enlace_acceso=data.enlace_acceso,
            fecha_publicacion=data.fecha_publicacion,
            estado=EstadoMaterial.BORRADOR
        )
        creado = self.repository.create(material)
        self._auditar(
            current_admin_id,
            TipoAccion.CREAR,
            f"Material externo creado {creado.nombre_material} tipo {creado.tipo_material}",
        )
        return self._map_response(creado)

    def create_archivo(self, nombre_material: str, descripcion: str, tipo_material: TipoMaterialEnum, fecha_publicacion: datetime, file: UploadFile, current_admin_id: int):
        if fecha_publicacion is None:
            raise BusinessRuleError("La fecha de publicación es requerida")
        if tipo_material in TIPOS_EXTERNOS or tipo_material in TIPOS_PRINCIPALES:
            raise BusinessRuleError("Use el endpoint correspondiente para este tipo de material")
        if fecha_publicacion and fecha_publicacion < datetime.now(timezone.utc):
            raise BusinessRuleError("La fecha de publicación debe ser igual o posterior a la actual")

        nombre_upper = nombre_material.upper()
        fecha_creacion = datetime.now(timezone.utc)
        extension = Path(file.filename).suffix
        nombre_supabase = self._generar_nombre_supabase(nombre_upper, extension, fecha_creacion)

        contenido = file.file.read()
        enlace = self.storage.upload_material(contenido, nombre_supabase, file.content_type)

        material = MaterialModel(
            nombre_material=nombre_upper,
            descripcion=descripcion,
            tipo_material=tipo_material,
            enlace_acceso=enlace,
            fecha_publicacion=fecha_publicacion,
            estado=EstadoMaterial.BORRADOR,
            fecha_creacion=fecha_creacion
        )
        creado = self.repository.create(material)
        self._auditar(
            current_admin_id,
            TipoAccion.CREAR,
            f"Material de archivo creado {creado.nombre_material} tipo {creado.tipo_material}",
        )
        return self._map_response(creado)

    def create_principal(self, id_convocatoria: int, tipo_material: TipoMaterialEnum, nombre_material: str, descripcion: str, file: UploadFile, current_admin_id: int):
        if tipo_material not in TIPOS_PRINCIPALES:
            raise BusinessRuleError("El tipo de material no es principal")
        convocatoria = self.convocatoria_repo.get_by_id(id_convocatoria)
        if not convocatoria: raise NotFoundError("Convocatoria no encontrada")

        existente = self.repository.get_material_principal(id_convocatoria, tipo_material)
        if existente:
            raise BusinessRuleError(f"La convocatoria ya tiene un material de tipo {tipo_material.value}. Reemplácelo o elimínelo primero.")

        nombre_upper = nombre_material.upper()
        fecha_creacion = datetime.now(timezone.utc)
        extension = Path(file.filename).suffix
        nombre_supabase = self._generar_nombre_supabase(nombre_upper, extension, fecha_creacion)

        contenido = file.file.read()
        enlace = self.storage.upload_material(contenido, f"{tipo_material.value}/{nombre_supabase}", file.content_type)

        material = MaterialModel(
            nombre_material=nombre_upper,
            descripcion=descripcion,
            tipo_material=tipo_material,
            enlace_acceso=enlace,
            fecha_publicacion=datetime.now(timezone.utc),
            estado=EstadoMaterial.PUBLICO,
            fecha_creacion=fecha_creacion
        )
        creado = self.repository.create(material)
        self.repository.link_convocatoria(creado.id_material, id_convocatoria)
        self._auditar(
            current_admin_id,
            TipoAccion.CREAR,
            f"Material principal creado {creado.nombre_material} tipo {creado.tipo_material} para convocatoria {convocatoria.nombre_convocatoria}",
        )
        return self._map_response(creado)

    def update(self, material_id: int, data: MaterialUpdateDTO, current_admin_id: int):
        material = self.repository.get_by_id(material_id)
        if not material:
            raise NotFoundError("Material no encontrado")

        if data.fecha_publicacion and data.fecha_publicacion < datetime.now(timezone.utc) and material.fecha_publicacion != data.fecha_publicacion:
            raise BusinessRuleError("La fecha de publicación debe ser igual o posterior a la actual")

        if material.estado == EstadoMaterial.PUBLICO:
            if any(v is not None for k, v in data.model_dump().items() if k not in ['nombre_material', 'descripcion']):
                raise BusinessRuleError("Solo nombre y descripción son editables en estado PUBLICO")

        if material.tipo_material in TIPOS_EXTERNOS and data.tipo_material is not None and data.tipo_material not in TIPOS_EXTERNOS:
            raise BusinessRuleError("No se puede cambiar un material externo a un tipo no externo.")

        effective_tipo = data.tipo_material if data.tipo_material is not None else material.tipo_material

        if effective_tipo in TIPOS_PRINCIPALES:
            if any([
                data.tipo_material is not None,
                data.fecha_publicacion is not None,
                data.enlace_acceso is not None,
            ]):
                raise BusinessRuleError("Solo se permite editar nombre y descripción para materiales principales.")

        if effective_tipo not in TIPOS_EXTERNOS and effective_tipo not in TIPOS_PRINCIPALES:
            if data.tipo_material is not None and (data.tipo_material in TIPOS_EXTERNOS or data.tipo_material in TIPOS_PRINCIPALES):
                raise BusinessRuleError("Solo se permite cambiar entre tipos que no sean externos ni principales.")

        if data.enlace_acceso is not None and effective_tipo not in TIPOS_EXTERNOS:
            raise BusinessRuleError("No se puede editar el enlace de acceso en materiales que no son externos.")
        
        old_nombre = material.nombre_material
        if data.nombre_material:
            material.nombre_material = data.nombre_material.upper()
        if data.descripcion is not None:
            material.descripcion = data.descripcion

        if material.estado in [EstadoMaterial.BORRADOR, EstadoMaterial.OCULTO]:
            if data.tipo_material is not None:
                material.tipo_material = data.tipo_material
            if material.tipo_material in TIPOS_EXTERNOS:
                if data.enlace_acceso:
                    material.enlace_acceso = data.enlace_acceso
            if data.fecha_publicacion is not None:
                material.fecha_publicacion = data.fecha_publicacion

        if old_nombre != material.nombre_material and material.tipo_material not in TIPOS_EXTERNOS:
            extension = Path(material.enlace_acceso).suffix
            nuevo_nombre_supa = self._generar_nombre_supabase(material.nombre_material, extension, material.fecha_creacion)
            if material.tipo_material in TIPOS_PRINCIPALES:
                nuevo_nombre_supa = f"{material.tipo_material.value}/{nuevo_nombre_supa}"
            try:
                nuevo_enlace = self.storage.rename_file(material.enlace_acceso, nuevo_nombre_supa)
                material.enlace_acceso = nuevo_enlace
            except BusinessRuleError:
                pass

        actualizado = self.repository.update(material)
        self._auditar(
            current_admin_id,
            TipoAccion.ACTUALIZAR,
            f"Material actualizado {actualizado.nombre_material} tipo {actualizado.tipo_material}",
        )
        return self._map_response(actualizado)

    def delete(self, material_id: int, current_admin_id: int):
        material = self.repository.get_by_id(material_id)
        if not material: raise NotFoundError("Material no encontrado")

        if material.tipo_material in TIPOS_PRINCIPALES and material.convocatorias:
            raise BusinessRuleError("No se puede eliminar un material principal asociado a una convocatoria")

        enlace = material.enlace_acceso
        descripcion = f"Material eliminado {material.nombre_material} tipo {material.tipo_material}"
        self.repository.delete(material)

        if material.tipo_material not in TIPOS_EXTERNOS:
            self.storage.delete_file(enlace)
        self._auditar(current_admin_id, TipoAccion.ELIMINAR, descripcion)
        
        return {"id_material": material_id}

    def cambiar_estado(self, material_id: int, nuevo_estado: EstadoMaterial, current_admin_id: int):
        material = self.repository.get_by_id(material_id)
        if not material: raise NotFoundError("Material no encontrado")
        estado_actual = material.estado

        if nuevo_estado == EstadoMaterial.BORRADOR:
            raise BusinessRuleError("No se puede regresar a BORRADOR")
        
        if material.tipo_material in TIPOS_PRINCIPALES and nuevo_estado == EstadoMaterial.OCULTO:
            raise BusinessRuleError("Materiales principales no pueden ser OCULTOS")

        if material.estado == EstadoMaterial.BORRADOR and nuevo_estado == EstadoMaterial.OCULTO:
            raise BusinessRuleError("Solo se puede ocultar un material PUBLICO")

        material.estado = nuevo_estado
        actualizado = self.repository.update(material)
        accion = TipoAccion.PUBLICAR if nuevo_estado == EstadoMaterial.PUBLICO else TipoAccion.OCULTAR
        self._auditar(
            current_admin_id,
            accion,
            f"Material {actualizado.nombre_material} cambio estado de {estado_actual} a {nuevo_estado}",
        )
        return self._map_response(actualizado)
    
    def link_material_principal_tipo(self, data: LinkMaterialPrincipalDTO, current_admin_id: int):
        material_nuevo = self.repository.get_by_id(data.id_material)
        material_antiguo = self.repository.get_material_principal(data.id_convocatoria, data.tipo_material)
        
        if not material_nuevo:
            raise NotFoundError("Material no encontrado")
        if material_nuevo.tipo_material != data.tipo_material:
            raise BusinessRuleError("El material no es del tipo esperado")
        if not material_antiguo:
            raise BusinessRuleError("No existe un material principal de este tipo")

        self.repository.unlink_convocatoria(material_antiguo.id_material, data.id_convocatoria)
        self.repository.link_convocatoria(material_nuevo.id_material, data.id_convocatoria)
        
        self._auditar(
            current_admin_id,
            TipoAccion.ACTUALIZAR,
            f"Material {data.tipo_material.value}: {material_nuevo.nombre_material} ligado a la convocatoria {data.id_convocatoria}",
        )
        return LinkMaterialPrincipalResponse(
            success=True,
            id_convocatoria=data.id_convocatoria,
            tipo_material=data.tipo_material.value,
            material_actual=self._map_response(material_nuevo)
        )

    def link_convocatoria(self, id_material: int, id_convocatoria: int, current_admin_id: int):
        material = self.repository.get_by_id(id_material)
        if not material: raise NotFoundError("Material no encontrado")
        convocatoria = self.convocatoria_repo.get_by_id(id_convocatoria)
        if not convocatoria: raise NotFoundError("Convocatoria no encontrada")

        if material.tipo_material in TIPOS_PRINCIPALES:
            existente = self.repository.get_material_principal(id_convocatoria, material.tipo_material)
            if existente: raise BusinessRuleError(f"Ya existe un material principal {material.tipo_material.value}")

        if self.repository.check_link_convocatoria(id_material, id_convocatoria):
            raise BusinessRuleError("El material ya está enlazado a esta convocatoria")

        self.repository.link_convocatoria(id_material, id_convocatoria)
        self._auditar(
            current_admin_id,
            TipoAccion.ACTUALIZAR,
            f"Material {material.nombre_material} enlazado a convocatoria {convocatoria.nombre_convocatoria}",
        )
        return {"success": True}

    def link_fase(self, id_material: int, id_fase: int, current_admin_id: int):
        material = self.repository.get_by_id(id_material)
        if not material: raise NotFoundError("Material no encontrado")
        if material.tipo_material in TIPOS_PRINCIPALES:
            raise BusinessRuleError("Materiales principales no pueden enlazarse a fases")
        if self.repository.check_link_fase(id_material, id_fase):
            raise BusinessRuleError("El material ya está enlazado a esta fase")

        self.repository.link_fase(id_material, id_fase)
        self._auditar(
            current_admin_id,
            TipoAccion.ACTUALIZAR,
            f"Material {material.nombre_material} enlazado a fase {id_fase}",
        )
        return {"success": True}

    def unlink_convocatoria(self, id_material: int, id_convocatoria: int, current_admin_id: int):
        material = self.repository.get_by_id(id_material)
        if not material: raise NotFoundError("Material no encontrado")
        convocatoria = self.convocatoria_repo.get_by_id(id_convocatoria)

        if material.tipo_material in TIPOS_PRINCIPALES and convocatoria and convocatoria.estado == EstadoConvocatoria.PUBLICADA:
            raise BusinessRuleError("No puede desligar un material principal de una convocatoria PUBLICADA")

        self.repository.unlink_convocatoria(id_material, id_convocatoria)
        self._auditar(
            current_admin_id,
            TipoAccion.ACTUALIZAR,
            f"Material {material.nombre_material} desligado de convocatoria {id_convocatoria}",
        )
        return {"success": True}

    def unlink_fase(self, id_material: int, id_fase: int, current_admin_id: int):
        material = self.repository.get_by_id(id_material)
        if not material: raise NotFoundError("Material no encontrado")
        self.repository.unlink_fase(id_material, id_fase)
        self._auditar(
            current_admin_id,
            TipoAccion.ACTUALIZAR,
            f"Material {material.nombre_material} desligado de fase {id_fase}",
        )
        return {"success": True}

    def _auditar(self, current_admin_id: int, accion: TipoAccion, descripcion: str):
        self.sistema_repository.create_auditoria(
            AuditoriaModel(
                id_administrador=current_admin_id,
                accion=accion,
                modulo=TipoModulo.MATERIAL,
                descripcion=descripcion,
            )
        )

    def get_public_materiales(
        self, page: int, limit: int, tipo_material: Optional[TipoMaterialEnum],
        fecha_start: Optional[datetime], fecha_end: Optional[datetime], busqueda: Optional[str]
    ):
        skip = (page - 1) * limit
        items, total = self.repository.get_public_materiales(
            skip, limit, tipo_material, fecha_start, fecha_end, busqueda
        )
        mapped_items = [
            {
                "nombre_material": item.nombre_material,
                "enlace_acceso": item.enlace_acceso,
                "descripcion": item.descripcion,
                "fecha_publicacion": item.fecha_publicacion
            } for item in items
        ]
        return mapped_items, total

    def get_public_by_convocatoria(self, id_convocatoria: int):
        items = self.repository.get_public_by_convocatoria(id_convocatoria)
        return [
            {
                "nombre_material": item.nombre_material,
                "descripcion": item.descripcion,
                "enlace_acceso": item.enlace_acceso,
                "tipo_material": item.tipo_material
            } for item in items
        ]

    def get_public_by_fase(self, id_fase: int):
        items = self.repository.get_public_by_fase(id_fase)
        return [
            {
                "nombre_material": item.nombre_material,
                "descripcion": item.descripcion,
                "enlace_acceso": item.enlace_acceso,
                "tipo_material": item.tipo_material
            } for item in items
        ]
    
    def get_material_principal_by_tipo(self, tipo_material: TipoMaterialEnum):
        if tipo_material not in TIPOS_PRINCIPALES:
            raise BusinessRuleError("El tipo de material no es principal")
        
        items = self.repository.get_materiales_principales_by_tipo(tipo_material)
        return [
            {
                "id_material":item.id_material,
                "nombre_material": item.nombre_material,
                "enlace_acceso": item.enlace_acceso,
                "tipo_material": item.tipo_material
            }
            for item in items
        ]
    
    def get_material_principal_by_convocatoria(self, id_convocatoria: int):
        materiales = self.repository.get_material_principal_by_convocatoria(id_convocatoria)
        return [
                {
                    "id_material": material.id_material,
                    "nombre_material": material.nombre_material,
                    "enlace_acceso": material.enlace_acceso,
                    "tipo_material": material.tipo_material
                } for material in materiales
            ] or []