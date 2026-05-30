from typing import Literal, Optional
from sqlalchemy import or_, asc, desc
from sqlalchemy.orm import Session

from app.modules.resultados.resultado_model import ResultadoModel
from app.modules.inscripciones.inscripcion_model import InscripcionModel
from app.modules.estudiantes.estudiante_model import EstudianteModel
from app.modules.fases.fase_model import FasePruebaModel

class ResultadoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, resultado_id: int):
        return self.db.query(ResultadoModel).filter(ResultadoModel.id_resultado == resultado_id).first()

    def get_by_id_y_fase(self, id_resultado: int, id_fase_prueba: int):
        return (
            self.db.query(ResultadoModel)
            .filter(
                ResultadoModel.id_resultado == id_resultado,
                ResultadoModel.id_fase_prueba == id_fase_prueba
            )
            .first()
        )
    def get_by_inscripcion_y_fase(self, id_inscripcion: int, id_fase_prueba: int):
        return (
            self.db.query(ResultadoModel)
            .filter(
                ResultadoModel.id_inscripcion == id_inscripcion,
                ResultadoModel.id_fase_prueba == id_fase_prueba
            )
            .first()
        )

    def get_all_by_fase(self, id_fase_prueba: int):
        return self.db.query(ResultadoModel).filter(ResultadoModel.id_fase_prueba == id_fase_prueba).all()

    def get_all_avanzado(
        self,
        skip: int,
        limit: int,
        search: Optional[str] = None,
        estado_aprobacion: Optional[Literal["APROBADO", "REPROBADO"]] = None,
        sort_by: Optional[Literal["nota", "apellido"]] = None,
        sort_order: Literal["asc", "desc"] = "desc"
    ):
        query = (
            self.db.query(ResultadoModel)
            .join(InscripcionModel, ResultadoModel.id_inscripcion == InscripcionModel.id_inscripcion)
            .join(EstudianteModel, InscripcionModel.id_estudiante == EstudianteModel.id_estudiante)
            .join(FasePruebaModel, ResultadoModel.id_fase_prueba == FasePruebaModel.id_fase)
        )

        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    EstudianteModel.carnet_identidad.ilike(search_filter),
                    EstudianteModel.nombres.ilike(search_filter),
                    EstudianteModel.paterno.ilike(search_filter),
                    EstudianteModel.materno.ilike(search_filter)
                )
            )

        if estado_aprobacion == "APROBADO":
            query = query.filter(ResultadoModel.nota >= FasePruebaModel.criterio_aprobacion)
        elif estado_aprobacion == "REPROBADO":
            query = query.filter(ResultadoModel.nota < FasePruebaModel.criterio_aprobacion)

        if sort_by == "nota":
            order_func = asc if sort_order == "asc" else desc
            query = query.order_by(order_func(ResultadoModel.nota))
        elif sort_by == "apellido":
            order_func = asc if sort_order == "asc" else desc
            query = query.order_by(order_func(EstudianteModel.paterno), order_func(EstudianteModel.materno))

        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def get_aprobados_by_fase(
        self,
        id_fase_prueba: int,
        sort_by: Literal["nombre", "paterno", "materno", "ci", "resultado"] = "resultado",
        sort_order: Literal["asc", "desc"] = "desc"
    ):
        query = (
            self.db.query(
                ResultadoModel.id_inscripcion,
                EstudianteModel.id_estudiante,
                EstudianteModel.carnet_identidad,
                EstudianteModel.nombres,
                EstudianteModel.paterno,
                EstudianteModel.materno,
                ResultadoModel.nota
            )
            .join(InscripcionModel, ResultadoModel.id_inscripcion == InscripcionModel.id_inscripcion)
            .join(EstudianteModel, InscripcionModel.id_estudiante == EstudianteModel.id_estudiante)
            .join(FasePruebaModel, ResultadoModel.id_fase_prueba == FasePruebaModel.id_fase)
            .filter(ResultadoModel.id_fase_prueba == id_fase_prueba)
            .filter(ResultadoModel.nota >= FasePruebaModel.criterio_aprobacion)
        )

        order_func = asc if sort_order == "asc" else desc

        if sort_by == "nombre":
            query = query.order_by(order_func(EstudianteModel.nombres))
        elif sort_by == "paterno":
            query = query.order_by(order_func(EstudianteModel.paterno))
        elif sort_by == "materno":
            query = query.order_by(order_func(EstudianteModel.materno))
        elif sort_by == "ci":
            query = query.order_by(order_func(EstudianteModel.carnet_identidad))
        elif sort_by == "resultado":
            query = query.order_by(order_func(ResultadoModel.nota))

        return query.all()

    def create(self, resultado: ResultadoModel):
        self.db.add(resultado)
        self.db.commit()
        self.db.refresh(resultado)
        return resultado

    def bulk_save(self, resultados: list[ResultadoModel]):
        self.db.add_all(resultados)
        self.db.commit()

    def update(self, resultado: ResultadoModel):
        self.db.commit()
        self.db.refresh(resultado)
        return resultado

    def bulk_update(self):
        self.db.commit()

    def delete(self, resultado: ResultadoModel):
        self.db.delete(resultado)
        self.db.commit()