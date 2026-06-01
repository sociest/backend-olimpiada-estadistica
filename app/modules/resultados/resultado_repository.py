from typing import Literal, Optional
from sqlalchemy import or_, asc, desc
from sqlalchemy.orm import Session

from app.modules.resultados.resultado_model import ResultadoModel, EstadoResultado
from app.modules.inscripciones.inscripcion_model import InscripcionModel
from app.modules.estudiantes.estudiante_model import EstudianteModel
from app.modules.fases.fase_model import FasePruebaModel
from sqlalchemy.orm import joinedload
from app.modules.categorias.categoria_model import CategoriaModel
from app.modules.convocatorias.convocatoria_model import ConvocatoriaModel
from app.modules.fases.fase_model import FaseModel

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
        id_fase_prueba: int,
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
            .filter(ResultadoModel.id_fase_prueba == id_fase_prueba)
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
        
    def get_fase_context_for_export(self, id_fase_prueba: int):
        return (
            self.db.query(FasePruebaModel, FaseModel, CategoriaModel, ConvocatoriaModel)
            .join(FaseModel, FasePruebaModel.id_fase == FaseModel.id_fase)
            .join(CategoriaModel, FaseModel.id_categoria_fk == CategoriaModel.id_categoria)
            .join(ConvocatoriaModel, CategoriaModel.id_convocatoria == ConvocatoriaModel.id_convocatoria)
            .filter(FasePruebaModel.id_fase == id_fase_prueba)
            .first()
        )

    def get_export_data(self, id_fase_prueba: int, estado_aprobacion: str = "TODOS"):
        query = (
            self.db.query(
                EstudianteModel.carnet_identidad,
                EstudianteModel.nombres,
                EstudianteModel.paterno,
                EstudianteModel.materno,
                ResultadoModel.nota.label("resultado")
            )
            .join(InscripcionModel, ResultadoModel.id_inscripcion == InscripcionModel.id_inscripcion)
            .join(EstudianteModel, InscripcionModel.id_estudiante == EstudianteModel.id_estudiante)
            .join(FasePruebaModel, ResultadoModel.id_fase_prueba == FasePruebaModel.id_fase)
            .filter(ResultadoModel.id_fase_prueba == id_fase_prueba)
        )

        if estado_aprobacion == "APROBADO":
            query = query.filter(ResultadoModel.nota >= FasePruebaModel.criterio_aprobacion)
        elif estado_aprobacion == "REPROBADO":
            query = query.filter(ResultadoModel.nota < FasePruebaModel.criterio_aprobacion)

        query = query.order_by(EstudianteModel.paterno.asc(), EstudianteModel.materno.asc(), EstudianteModel.nombres.asc())
        return query.all()

    def get_contexto_importacion(self, id_fase_prueba: int):
        fase_info = (
            self.db.query(FasePruebaModel, FaseModel)
            .join(FaseModel, FasePruebaModel.id_fase == FaseModel.id_fase)
            .filter(FasePruebaModel.id_fase == id_fase_prueba)
            .first()
        )
        
        if not fase_info:
            return None, None, None
            
        fase_prueba, fase_base = fase_info
        id_categoria = fase_base.id_categoria_fk

        inscripciones_raw = (
            self.db.query(InscripcionModel, EstudianteModel.carnet_identidad)
            .join(EstudianteModel, InscripcionModel.id_estudiante == EstudianteModel.id_estudiante)
            .filter(InscripcionModel.id_categoria == id_categoria)
            .all()
        )
        dict_inscripciones = {ci: inscripcion for inscripcion, ci in inscripciones_raw}

        resultados_raw = (
            self.db.query(ResultadoModel.id_inscripcion, ResultadoModel.nota)
            .filter(ResultadoModel.id_fase_prueba == id_fase_prueba)
            .all()
        )
        dict_resultados_existentes = {res.id_inscripcion: res.nota for res in resultados_raw}

        return id_categoria, dict_inscripciones, dict_resultados_existentes
    
    def get_public_resultados_finales(
        self,
        skip: int,
        limit: int,
        id_convocatoria: Optional[int],
        id_categoria: Optional[int]
    ):
        query = (
            self.db.query(
                EstudianteModel.nombres,
                EstudianteModel.paterno,
                EstudianteModel.materno,
                EstudianteModel.carnet_identidad,
                ResultadoModel.nota
            )
            .join(InscripcionModel, ResultadoModel.id_inscripcion == InscripcionModel.id_inscripcion)
            .join(EstudianteModel, InscripcionModel.id_estudiante == EstudianteModel.id_estudiante)
            .join(FasePruebaModel, ResultadoModel.id_fase_prueba == FasePruebaModel.id_fase)
            .join(CategoriaModel, ResultadoModel.id_categoria == CategoriaModel.id_categoria)
            .filter(
                ResultadoModel.estado == EstadoResultado.PUBLICADO,
                FasePruebaModel.es_prueba_final == True
            )
        )

        if id_categoria:
            query = query.filter(CategoriaModel.id_categoria == id_categoria)
        
        if id_convocatoria:
            query = query.filter(CategoriaModel.id_convocatoria == id_convocatoria)

        total = query.count()
        items = query.order_by(desc(ResultadoModel.nota)).offset(skip).limit(limit).all()
        return items, total

    def get_public_resultados_by_fase(self, id_fase: int):
        return (
            self.db.query(
                EstudianteModel.carnet_identidad,
                ResultadoModel.nota,
                ResultadoModel.observaciones
            )
            .join(InscripcionModel, ResultadoModel.id_inscripcion == InscripcionModel.id_inscripcion)
            .join(EstudianteModel, InscripcionModel.id_estudiante == EstudianteModel.id_estudiante)
            .filter(
                ResultadoModel.id_fase_prueba == id_fase,
                ResultadoModel.estado == EstadoResultado.PUBLICADO
            )
            .order_by(asc(EstudianteModel.carnet_identidad))
            .all()
        )