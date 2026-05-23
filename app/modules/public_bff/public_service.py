import asyncio

from app.modules.avisos.aviso_service import AvisoService
from app.modules.categorias.categoria_service import CategoriaService
from app.modules.convocatorias.convocatoria_service import ConvocatoriaService
from app.modules.fases.fase_service import FaseService
from app.modules.materiales.material_service import MaterialService
from app.modules.personas.persona_service import PersonaService
from app.modules.colegios.colegio_service import ColegioService


class PublicBffService:
    def __init__(
        self,
        convocatoria_service: ConvocatoriaService,
        categoria_service: CategoriaService,
        aviso_service: AvisoService,
        material_service: MaterialService,
        fase_service: FaseService,
        persona_service: PersonaService,
        colegio_service: ColegioService,
    ):
        self.convocatoria_service = convocatoria_service
        self.categoria_service = categoria_service
        self.aviso_service = aviso_service
        self.material_service = material_service
        self.fase_service = fase_service
        self.persona_service = persona_service
        self.colegio_service = colegio_service

    async def get_inicio(self):
        convocatoria = await asyncio.to_thread(self._safe_get_convocatoria)
        avisos_task = asyncio.to_thread(self.aviso_service.get_recientes, 4)

        if convocatoria is None:
            avisos = await avisos_task
            return {
                "convocatoria": None,
                "material_principal": self._format_material_principal(None),
                "categorias": [],
                "avisos": self._format_avisos(avisos or []),
            }

        categorias_task = asyncio.to_thread(
            self.categoria_service.get_resumen_by_convocatoria, convocatoria.id_convocatoria
        )
        material_principal_task = asyncio.to_thread(
            self._safe_get_material_principal_inicio,
            convocatoria.id_convocatoria,
        )
        categorias, avisos, material_principal = await asyncio.gather(categorias_task, avisos_task, material_principal_task)
        return {
            "convocatoria": convocatoria,
            "material_principal": self._format_material_principal(material_principal),
            "categorias": self._format_categorias_inicio(convocatoria, categorias or []),
            "avisos": self._format_avisos(avisos or []),
        }

    async def get_personal(self, tipo: str):
        try:
            items, _ = await asyncio.to_thread(
                self.persona_service.get_personal_by_tipo, tipo, 1, 1000
            )
        except Exception:
            return []
        return items or []

    async def get_convocatoria_detalle(self, convocatoria_id: int):
        convocatoria = await asyncio.to_thread(self._safe_get_convocatoria_by_id, convocatoria_id)
        if convocatoria is None:
            return {
                "convocatoria": None,
                "categorias": [],
                "materiales": [],
                "afiche": None,
                "convocatoria_documento": None,
                "reglamento": None,
            }
        categorias_task = asyncio.to_thread(
            self.categoria_service.get_resumen_by_convocatoria, convocatoria_id
        )
        materiales_task = asyncio.to_thread(self.material_service.get_public_by_convocatoria, convocatoria_id, 1, 100)
        afiche_task = asyncio.to_thread(
            self._safe_get_material_principal_public,
            convocatoria_id,
            "AFICHE",
        )
        convocatoria_doc_task = asyncio.to_thread(
            self._safe_get_material_principal_public,
            convocatoria_id,
            "CONVOCATORIA",
        )
        reglamento_task = asyncio.to_thread(
            self._safe_get_material_principal_public,
            convocatoria_id,
            "REGLAMENTO",
        )
        categorias, materiales_data, afiche, convocatoria_doc, reglamento = await asyncio.gather(
            categorias_task,
            materiales_task,
            afiche_task,
            convocatoria_doc_task,
            reglamento_task,
        )
        materiales = materiales_data[0]
        return {
            "convocatoria": convocatoria,
            "categorias": self._format_categorias_detalle(categorias or []),
            "materiales": self._format_materiales_simples(materiales or []),
            "afiche": self._format_material_principal_detalle(afiche),
            "convocatoria_documento": self._format_material_principal_detalle(convocatoria_doc),
            "reglamento": self._format_material_principal_detalle(reglamento),
        }

    async def get_fases_por_categoria(self, categoria_id: int):
        try:
            items, _ = await asyncio.to_thread(
                self.fase_service.get_by_categoria, categoria_id, 1, 1000
            )
        except Exception:
            return []
        fases = [self._format_fase_publica(fase) for fase in items or []]
        return [fase for fase in fases if fase is not None]

    async def get_materiales_por_fase(self, fase_id: int):
        try:
            items, _ = await asyncio.to_thread(
                self.material_service.get_public_by_fase, fase_id, 1, 1000
            )
        except Exception:
            return []
        return items or []

    def _safe_get_convocatoria(self):
        try:
            return self.convocatoria_service.get_activa_o_reciente()
        except Exception:
            return None

    def _safe_get_convocatoria_by_id(self, convocatoria_id: int):
        try:
            return self.convocatoria_service.get_by_id(convocatoria_id)
        except Exception:
            return None

    def _safe_get_material_principal_public(self, convocatoria_id: int, importancia_tipo: str):
        try:
            return self.material_service.get_material_principal_public(convocatoria_id, importancia_tipo)
        except Exception:
            return None

    def _safe_get_material_principal_inicio(self, convocatoria_id: int):
        for importancia_tipo in ("AFICHE", "CONVOCATORIA"):
            material = self._safe_get_material_principal_public(convocatoria_id, importancia_tipo)
            if material is not None:
                return material
        return None

    def _format_material_principal(self, material):
        if material is None:
            return {
                "enlace_acceso": None,
                "mensaje": "No existe material principal AFICHE o CONVOCATORIA para la convocatoria",
            }
        return {
            "enlace_acceso": material.enlace_acceso,
            "mensaje": None,
        }

    def _format_categorias_inicio(self, convocatoria, categorias):
        return [
            {
                "nombre_categoria": categoria["nombre_categoria"] if isinstance(categoria, dict) else categoria.nombre_categoria,
                "nivel": categoria["nivel"] if isinstance(categoria, dict) else categoria.nivel,
                "curso": categoria["curso"] if isinstance(categoria, dict) else categoria.curso,
                "id_categoria": categoria["id_categoria"] if isinstance(categoria, dict) else categoria.id_categoria,
            }
            for categoria in categorias
        ]

    def _format_categorias_detalle(self, categorias):
        return [
            {
                "id_categoria": categoria["id_categoria"] if isinstance(categoria, dict) else categoria.id_categoria,
                "nombre_categoria": categoria["nombre_categoria"] if isinstance(categoria, dict) else categoria.nombre_categoria,
                "nivel": categoria["nivel"] if isinstance(categoria, dict) else categoria.nivel,
                "curso": categoria["curso"] if isinstance(categoria, dict) else categoria.curso,
            }
            for categoria in categorias
        ]

    def _format_material_principal_detalle(self, material):
        if material is None:
            return None
        return {
            "enlace_acceso": material.enlace_acceso,
            "nombre_material": material.nombre_material,
            "descripcion": material.descripcion,
        }

    def _format_materiales_simples(self, materiales):
        return [
            {
                "enlace_acceso": material.enlace_acceso,
                "nombre_material": material.nombre_material,
                "descripcion": material.descripcion,
            }
            for material in materiales
        ]

    def _format_fase_publica(self, fase):
        fase_prueba = self.fase_service.repository.get_fase_prueba(fase.id_fase)
        if fase_prueba is not None:
            return {
                "id_fase": fase.id_fase,
                "id_categoria_fk": fase.id_categoria_fk,
                "nombre_fase": fase.nombre_fase,
                "descripcion": fase.descripcion,
                "modalidad": fase.modalidad,
                "estado": fase.estado,
                "tipo_fase": "PRUEBA",
                "id_fase_anterior": fase_prueba.id_fase_anterior,
                "criterio_aprobacion": fase_prueba.criterio_aprobacion,
                "fecha_realizacion": fase_prueba.fecha_realizacion,
                "lugar_realizacion": fase_prueba.lugar_realizacion,
            }

        fase_preparacion = self.fase_service.repository.get_fase_preparacion(fase.id_fase)
        if fase_preparacion is not None:
            return {
                "id_fase": fase.id_fase,
                "id_categoria_fk": fase.id_categoria_fk,
                "nombre_fase": fase.nombre_fase,
                "descripcion": fase.descripcion,
                "modalidad": fase.modalidad,
                "estado": fase.estado,
                "tipo_fase": "PREPARACION",
                "fecha_inicio": fase_preparacion.fecha_inicio,
                "fecha_fin": fase_preparacion.fecha_fin,
            }

        return None

    def _format_avisos(self, avisos):
        return [
            {
                "titulo": aviso.titulo,
                "descripcion": aviso.descripcion,
                "tipo": aviso.tipo,
                "fecha_publicacion": aviso.fecha_publicacion.date() if aviso.fecha_publicacion else None,
            }
            for aviso in avisos
        ]
    
    async def get_colegios_minified(self):
        try:
            items = await asyncio.to_thread(self.colegio_service.get_all_minified)
        except Exception:
            return []

        return [
            {
                "id_colegio": item.id_colegio,
                "nombre": item.nombre,
                "municipio": item.municipio,
                "turno": item.turno
            }
            for item in items or []
        ]
