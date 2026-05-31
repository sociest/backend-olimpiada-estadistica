from datetime import date, datetime
from sqlalchemy import func
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, case
from app.modules.categorias.categoria_model import CategoriaModel
from app.modules.colegios.colegio_model import ColegioModel
from app.modules.convocatorias.convocatoria_model import ConvocatoriaModel
from app.modules.inscripciones.inscripcion_model import InscripcionModel
from app.modules.inscripciones.inscripcion_model import EstadoInscripcion
from app.modules.estudiantes.estudiante_model import EstudianteModel
from app.modules.personas.persona_model import PersonaModel

class InscripcionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_convocatoria(self, convocatoria_id: int):
        return self.db.query(ConvocatoriaModel).filter(ConvocatoriaModel.id_convocatoria == convocatoria_id).first()

    def get_categoria(self, categoria_id: int):
        return self.db.query(CategoriaModel).filter(CategoriaModel.id_categoria == categoria_id).first()

    def buscar_categoria_automatica(self, convocatoria_id: int, curso: int, nivel):
        return self.db.query(CategoriaModel).filter(
            CategoriaModel.id_convocatoria == convocatoria_id,
            CategoriaModel.nivel == nivel,
            CategoriaModel.curso == curso
        ).first()

    def get_colegio(self, colegio_id: int):
        return self.db.query(ColegioModel).filter(ColegioModel.id_colegio == colegio_id).first()

    def get_estudiante_by_id(self, estudiante_id: int):
        return self.db.query(EstudianteModel).filter(EstudianteModel.id_estudiante == estudiante_id).first()

    def get_estudiante_by_ci(self, carnet_identidad: str):
        return (
            self.db.query(EstudianteModel, PersonaModel)
            .join(PersonaModel, EstudianteModel.id_estudiante == PersonaModel.id_persona)
            .filter(EstudianteModel.carnet_identidad == carnet_identidad)
            .first()
        )

    def get_estudiante_by_ci_fecha(self, carnet_identidad: str, fecha_nacimiento: date):
        return (
            self.db.query(EstudianteModel, PersonaModel)
            .join(PersonaModel, EstudianteModel.id_estudiante == PersonaModel.id_persona)
            .filter(EstudianteModel.carnet_identidad == carnet_identidad)
            .filter(EstudianteModel.fecha_nacimiento == fecha_nacimiento)
            .first()
        )

    def create_persona(self, persona: PersonaModel):
        self.db.add(persona)
        self.db.flush()
        return persona

    def create_estudiante(self, estudiante: EstudianteModel):
        self.db.add(estudiante)
        self.db.flush()
        return estudiante

    def get_inscripcion_existente(self, estudiante_id: int, convocatoria_id: int):
        return (
            self.db.query(InscripcionModel)
            .filter(InscripcionModel.id_estudiante == estudiante_id)
            .filter(InscripcionModel.id_convocatoria == convocatoria_id)
            .first()
        )

    def get_by_id(self, inscripcion_id: int):
        return self.db.query(InscripcionModel).filter(InscripcionModel.id_inscripcion == inscripcion_id).first()

    def create_inscripcion(self, inscripcion: InscripcionModel):
        self.db.add(inscripcion)
        self.db.flush()
        return inscripcion

    def list_inscripciones_avanzado(
        self,
        skip: int,
        limit: int,
        id_colegio: Optional[int] = None,
        id_categoria: Optional[int] = None,
        estado: Optional[EstadoInscripcion] = None,
        search_nombre: Optional[str] = None,
        search_documento: Optional[str] = None,
        fecha_inicio: Optional[datetime] = None,
        fecha_fin: Optional[datetime] = None
    ):
        query = self.db.query(InscripcionModel).join(EstudianteModel).join(PersonaModel)

        if id_colegio:
            query = query.filter(EstudianteModel.id_colegio == id_colegio)
        if id_categoria:
            query = query.filter(InscripcionModel.id_categoria == id_categoria)
        if estado:
            query = query.filter(InscripcionModel.estado == estado)
        if fecha_inicio:
            query = query.filter(InscripcionModel.fecha_inscripcion >= fecha_inicio)
        if fecha_fin:
            query = query.filter(InscripcionModel.fecha_inscripcion <= fecha_fin)
        
        if search_nombre:
            query = query.filter(
                or_(
                    PersonaModel.nombres.ilike(f"%{search_nombre}%"),
                    PersonaModel.paterno.ilike(f"%{search_nombre}%"),
                    PersonaModel.materno.ilike(f"%{search_nombre}%")
                )
            )
            
        if search_documento:
            query = query.filter(
                or_(
                    EstudianteModel.carnet_identidad == search_documento,
                    EstudianteModel.rude == search_documento
                )
            )

        orden_ponderado = case(
            (InscripcionModel.estado == EstadoInscripcion.PENDIENTE, 1),
            (InscripcionModel.estado == EstadoInscripcion.APROBADO, 2),
            (InscripcionModel.estado == EstadoInscripcion.RECHAZADO, 3),
            else_=4
        )
        
        query = query.order_by(orden_ponderado, InscripcionModel.fecha_inscripcion.desc())
        
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def delete(self, inscripcion: InscripcionModel):
        self.db.delete(inscripcion)

    def commit(self):
        self.db.commit()
    
    def get_datos_exportacion(self, ids: list[int]):
        return (
            self.db.query(
                EstudianteModel.carnet_identidad,
                PersonaModel.nombres,
                PersonaModel.paterno,
                PersonaModel.materno,
                ColegioModel.nombre.label("colegio_nombre"),
                CategoriaModel.nombre_categoria.label("categoria_nombre"),
                InscripcionModel.estado
            )
            .join(EstudianteModel, InscripcionModel.id_estudiante == EstudianteModel.id_estudiante)
            .join(PersonaModel, EstudianteModel.id_estudiante == PersonaModel.id_persona)
            .join(ColegioModel, EstudianteModel.id_colegio == ColegioModel.id_colegio)
            .join(CategoriaModel, InscripcionModel.id_categoria == CategoriaModel.id_categoria)
            .filter(InscripcionModel.id_inscripcion.in_(ids))
            .all()
        )
    
    def get_estadisticas_inscripcion(self, convocatoria_id: int) -> dict:
        resultados = (
            self.db.query(
                func.count(InscripcionModel.id_inscripcion).label("total"),
                func.sum(
                    case((InscripcionModel.estado == EstadoInscripcion.APROBADO, 1), else_=0)
                ).label("aprobados"),
                func.sum(
                    case((InscripcionModel.estado == EstadoInscripcion.PENDIENTE, 1), else_=0)
                ).label("pendientes"),
            )
            .filter(InscripcionModel.id_convocatoria == convocatoria_id)
            .first()
        )
        return {
            "total": resultados.total or 0,
            "aprobados": resultados.aprobados or 0,
            "pendientes": resultados.pendientes or 0,
        }
