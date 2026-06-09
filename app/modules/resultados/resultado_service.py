from sqlalchemy.orm import Session
from app.core.exceptions import BusinessRuleError, NotFoundError
from app.modules.resultados.resultado_model import EstadoResultado, ResultadoModel
from app.modules.resultados.resultado_repository import ResultadoRepository
from app.modules.resultados.resultado_schema import (
    ResultadoCreateDTO,
    ResultadoEstadoUpdateDTO,
    ResultadoMasivoCreateDTO,
    ResultadoMasivoUpdateDTO,
    ResultadoUpdateDTO
)
from app.modules.sistema.sistema_model import AuditoriaModel, TipoAccion, TipoModulo
from app.modules.sistema.sistema_repository import SistemaRepository
from typing import Optional

class ResultadoService:
    def __init__(self, db: Session):
        self.repository = ResultadoRepository(db)
        self.sistema_repository = SistemaRepository(db)

    def get_by_id(self, resultado_id: int):
        resultado = self.repository.get_by_id(resultado_id)
        if not resultado:
            raise NotFoundError("Resultado no encontrado")
        return resultado

    def get_all(self, id_fase_prueba: int, page: int, limit: int, search: str, estado_aprobacion: str, sort_by: str, sort_order: str):
        skip = (page - 1) * limit
        items, total = self.repository.get_all_avanzado(
            id_fase_prueba=id_fase_prueba,
            skip=skip,
            limit=limit,
            search=search,
            estado_aprobacion=estado_aprobacion,
            sort_by=sort_by,
            sort_order=sort_order
        )
        mapped_items = []
        for resultado, ci, nombres, paterno, materno in items:
            mapped_items.append({
                "id_resultado": resultado.id_resultado,
                "id_categoria": resultado.id_categoria,
                "id_fase_prueba": resultado.id_fase_prueba,
                "id_inscripcion": resultado.id_inscripcion,
                "nota": resultado.nota,
                "observaciones": resultado.observaciones,
                "estado": resultado.estado,
                "carnet_identidad": ci,
                "nombres": nombres,
                "paterno": paterno,
                "materno": materno,
            })
        return mapped_items, total

    def get_aprobados_fase(self, id_fase_prueba: int, sort_by: str, sort_order: str):
        rows = self.repository.get_aprobados_by_fase(id_fase_prueba, sort_by, sort_order)
        return [
            {
                "id_inscripcion": r.id_inscripcion,
                "id_estudiante": r.id_estudiante,
                "carnet_identidad": r.carnet_identidad,
                "nombres": r.nombres,
                "paterno": r.paterno,
                "materno": r.materno,
                "nota": r.nota
            }
            for r in rows
        ]

    def create(self, data: ResultadoCreateDTO, current_admin_id: int):
        existente = self.repository.get_by_inscripcion_y_fase(data.id_inscripcion, data.id_fase_prueba)
        if existente:
            raise BusinessRuleError("Ya existe un resultado para esta inscripción en esta fase.")

        resultado = ResultadoModel(
            id_categoria=data.id_categoria,
            id_fase_prueba=data.id_fase_prueba,
            id_inscripcion=data.id_inscripcion,
            nota=data.nota,
            observaciones=data.observaciones,
            estado=EstadoResultado.BORRADOR
        )
        created = self.repository.create(resultado)
        self._auditar(
            current_admin_id,
            TipoAccion.CREAR,
            f"Resultado creado para inscripcion {created.id_inscripcion} en fase {created.id_fase_prueba}",
        )
        return created

    def create_masivo(self, data: ResultadoMasivoCreateDTO, current_admin_id: int):
        nuevos_resultados = []
        for id_insc in data.ids_inscripciones:
            existente = self.repository.get_by_inscripcion_y_fase(id_insc, data.id_fase_prueba)
            if not existente:
                nuevos_resultados.append(
                    ResultadoModel(
                        id_categoria=data.id_categoria,
                        id_fase_prueba=data.id_fase_prueba,
                        id_inscripcion=id_insc,
                        nota=0,
                        observaciones="",
                        estado=EstadoResultado.BORRADOR
                    )
                )
        if nuevos_resultados:
            self.repository.bulk_save(nuevos_resultados)
            self._auditar(
                current_admin_id,
                TipoAccion.CREAR,
                f"Resultados masivos creados: {len(nuevos_resultados)} en fase {data.id_fase_prueba}",
            )
        return len(nuevos_resultados)

    def update(self, resultado_id: int, data: ResultadoUpdateDTO, current_admin_id: int):
        resultado = self.get_by_id(resultado_id)

        if resultado.estado == EstadoResultado.PUBLICADO:
            raise BusinessRuleError("No se pueden hacer cambios en resultados con estado PUBLICADO.")

        updates = data.model_dump(exclude_unset=True)
        for key, value in updates.items():
            setattr(resultado, key, value)

        updated = self.repository.update(resultado)
        self._auditar(
            current_admin_id,
            TipoAccion.ACTUALIZAR,
            f"Resultado actualizado {updated.id_resultado} para inscripcion {updated.id_inscripcion}",
        )
        return updated

    def update_masivo(self, data: ResultadoMasivoUpdateDTO, current_admin_id: int):
        actualizados = 0
        for item in data.resultados:
            resultado = self.repository.get_by_id_y_fase(item.id_resultado, data.id_fase_prueba)
            if resultado and resultado.estado != EstadoResultado.PUBLICADO:
                resultado.nota = item.nota
                if item.observaciones is not None:
                    resultado.observaciones = item.observaciones
                actualizados += 1

        if actualizados > 0:
            self.repository.bulk_update()
            self._auditar(
                current_admin_id,
                TipoAccion.ACTUALIZAR,
                f"Resultados masivos actualizados: {actualizados} en fase {data.id_fase_prueba}",
            )
        return actualizados

    def cambiar_estado_individual(self, resultado_id: int, data: ResultadoEstadoUpdateDTO, current_admin_id: int):
        resultado = self.get_by_id(resultado_id)
        estado_actual = resultado.estado
        nuevo_estado = data.estado

        if nuevo_estado == EstadoResultado.BORRADOR:
            raise BusinessRuleError("No se puede regresar al estado BORRADOR bajo ninguna circunstancia.")
        
        if estado_actual == EstadoResultado.BORRADOR and nuevo_estado == EstadoResultado.OCULTO:
            raise BusinessRuleError("De BORRADOR solo se puede pasar a PUBLICADO.")
        
        if estado_actual == EstadoResultado.PUBLICADO and nuevo_estado == EstadoResultado.OCULTO:
            raise BusinessRuleError("Solo la ruta de fase masiva puede ocultar resultados. Use la ruta de fase.")

        resultado.estado = nuevo_estado
        updated = self.repository.update(resultado)
        accion = TipoAccion.PUBLICAR if nuevo_estado == EstadoResultado.PUBLICADO else TipoAccion.OCULTAR
        self._auditar(
            current_admin_id,
            accion,
            f"Resultado {updated.id_resultado} cambio estado de {estado_actual} a {nuevo_estado}",
        )
        return updated

    def publicar_fase(self, id_fase_prueba: int, current_admin_id: int):
        resultados = self.repository.get_all_by_fase(id_fase_prueba)
        for res in resultados:
            if res.estado == EstadoResultado.BORRADOR or res.estado == EstadoResultado.OCULTO:
                res.estado = EstadoResultado.PUBLICADO
        self.repository.bulk_update()
        self._auditar(
            current_admin_id,
            TipoAccion.PUBLICAR,
            f"Resultados publicados para fase {id_fase_prueba}: {len(resultados)} registros",
        )
        return len(resultados)

    def ocultar_fase(self, id_fase_prueba: int, current_admin_id: int):
        resultados = self.repository.get_all_by_fase(id_fase_prueba)
        for res in resultados:
            if res.estado == EstadoResultado.PUBLICADO:
                res.estado = EstadoResultado.OCULTO
        self.repository.bulk_update()
        self._auditar(
            current_admin_id,
            TipoAccion.OCULTAR,
            f"Resultados ocultados para fase {id_fase_prueba}: {len(resultados)} registros",
        )
        return len(resultados)

    def _auditar(self, current_admin_id: int, accion: TipoAccion, descripcion: str):
        self.sistema_repository.create_auditoria(
            AuditoriaModel(
                id_administrador=current_admin_id,
                accion=accion,
                modulo=TipoModulo.RESULTADO,
                descripcion=descripcion,
            )
        )

    def get_public_resultados_finales(
        self,
        page: int,
        limit: int,
        id_convocatoria: Optional[int],
        id_categoria: Optional[int]
    ):
        skip = (page - 1) * limit
        items, total = self.repository.get_public_resultados_finales(
            skip, limit, id_convocatoria, id_categoria
        )
        mapped_items = [
            {
                "nombres": item.nombres,
                "paterno": item.paterno,
                "materno": item.materno,
                "carnet_identidad": item.carnet_identidad,
                "nota": item.nota
            }
            for item in items
        ]
        return mapped_items, total

    def get_public_resultados_by_fase(self, id_fase: int):
        items = self.repository.get_public_resultados_by_fase(id_fase)
        return [
            {
                "carnet_identidad": item.carnet_identidad,
                "nota": item.nota,
                "observaciones": item.observaciones
            }
            for item in items
        ]