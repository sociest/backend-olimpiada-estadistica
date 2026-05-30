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
from app.modules.fases.fase_repository import FaseRepository 

class ResultadoService:
    def __init__(self, db: Session):
        self.repository = ResultadoRepository(db)
        self.fase_repository = FaseRepository(db)

    def get_by_id(self, resultado_id: int):
        resultado = self.repository.get_by_id(resultado_id)
        if not resultado:
            raise NotFoundError("Resultado no encontrado")
        return resultado

    def get_all(self, page: int, limit: int, search: str, estado_aprobacion: str, sort_by: str, sort_order: str):
        skip = (page - 1) * limit
        return self.repository.get_all_avanzado(
            skip=skip,
            limit=limit,
            search=search,
            estado_aprobacion=estado_aprobacion,
            sort_by=sort_by,
            sort_order=sort_order
        )
    
    def get_by_fase(self, id_fase_prueba: int, page: int, limit: int):
        skip = (page - 1) * limit
        return self.repository.get_all_by_fase(id_fase_prueba, skip, limit)

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

    def create(self, data: ResultadoCreateDTO):
        existente = self.repository.get_by_inscripcion_y_fase(data.id_inscripcion, data.id_fase_prueba)
        if existente:
            raise BusinessRuleError("Ya existe un resultado para esta inscripción en esta fase.")
        fase = self.fase_repository.get_by_id(data.id_fase_prueba)
        if not fase:
            raise BusinessRuleError("La fase de prueba no existe.")

        resultado = ResultadoModel(
            id_categoria=data.id_categoria,
            id_fase_prueba=data.id_fase_prueba,
            id_inscripcion=data.id_inscripcion,
            nota=data.nota,
            observaciones=data.observaciones,
            estado=EstadoResultado.BORRADOR
        )
        return self.repository.create(resultado)

    def create_masivo(self, data: ResultadoMasivoCreateDTO):
        fase = self.fase_repository.get_by_id(data.id_fase_prueba)
        if not fase:
            raise BusinessRuleError("La fase de prueba no existe.")
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
        return len(nuevos_resultados)

    def update(self, resultado_id: int, data: ResultadoUpdateDTO):
        resultado = self.get_by_id(resultado_id)

        if resultado.estado == EstadoResultado.PUBLICADO:
            raise BusinessRuleError("No se pueden hacer cambios en resultados con estado PUBLICADO.")

        updates = data.model_dump(exclude_unset=True)
        for key, value in updates.items():
            setattr(resultado, key, value)

        return self.repository.update(resultado)

    def update_masivo(self, data: ResultadoMasivoUpdateDTO):
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
        return actualizados

    def cambiar_estado_individual(self, resultado_id: int, data: ResultadoEstadoUpdateDTO):
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
        return self.repository.update(resultado)

    def publicar_fase(self, id_fase_prueba: int):
        resultados = self.repository.get_all_by_fase(id_fase_prueba)
        for res in resultados:
            if res.estado == EstadoResultado.BORRADOR or res.estado == EstadoResultado.OCULTO:
                res.estado = EstadoResultado.PUBLICADO
        self.repository.bulk_update()
        return len(resultados)

    def ocultar_fase(self, id_fase_prueba: int):
        resultados = self.repository.get_all_by_fase(id_fase_prueba)
        for res in resultados:
            if res.estado == EstadoResultado.PUBLICADO:
                res.estado = EstadoResultado.OCULTO
        self.repository.bulk_update()
        return len(resultados)