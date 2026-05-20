from datetime import date

from sqlalchemy.orm import Session

from app.modules.categorias.categoria_model import CategoriaModel
from app.modules.colegios.colegio_model import ColegioModel
from app.modules.convocatorias.convocatoria_model import ConvocatoriaModel
from app.modules.inscripciones.inscripcion_model import InscripcionModel
from app.modules.personas.persona_model import EstudianteModel, PersonaModel


class InscripcionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_convocatoria(self, convocatoria_id: int):
        return self.db.query(ConvocatoriaModel).filter(ConvocatoriaModel.id_convocatoria == convocatoria_id).first()

    def get_categoria(self, categoria_id: int):
        return self.db.query(CategoriaModel).filter(CategoriaModel.id_categoria == categoria_id).first()

    def get_colegio(self, colegio_id: int):
        return self.db.query(ColegioModel).filter(ColegioModel.id_colegio == colegio_id).first()

    def get_colegio_by_codigo(self, codigo: int):
        return self.db.query(ColegioModel).filter(ColegioModel.codigo == codigo).first()

    def create_colegio(self, colegio: ColegioModel):
        self.db.add(colegio)
        self.db.flush()
        return colegio

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

    def create_inscripcion(self, inscripcion: InscripcionModel):
        self.db.add(inscripcion)
        self.db.flush()
        return inscripcion

    def list_all(self, skip: int, limit: int):
        return self.db.query(InscripcionModel).offset(skip).limit(limit).all()

    def count_all(self):
        return self.db.query(InscripcionModel).count()
