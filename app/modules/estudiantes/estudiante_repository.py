from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, extract
from app.modules.estudiantes.estudiante_model import EstudianteModel
from app.modules.personas.persona_model import PersonaModel

class EstudianteRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_base_query(self):
        return self.db.query(EstudianteModel).join(PersonaModel)

    def create_persona(self, persona: PersonaModel):
        self.db.add(persona)
        self.db.flush()
        return persona

    def create_estudiante(self, estudiante: EstudianteModel):
        self.db.add(estudiante)
        return estudiante

    def get_by_id(self, estudiante_id: int):
        return self.get_base_query().filter(EstudianteModel.id_estudiante == estudiante_id).first()

    def get_by_ids(self, ids: list[int]):
        return self.get_base_query().filter(EstudianteModel.id_estudiante.in_(ids)).all()

    def get_persona_by_id(self, persona_id: int):
        return self.db.query(PersonaModel).filter(PersonaModel.id_persona == persona_id).first()

    def list_estudiantes(
        self, 
        skip: int, 
        limit: int,
        search: Optional[str] = None,
        carnet: Optional[str] = None,
        telefono: Optional[int] = None,
        rude: Optional[str] = None,
        mes_nacimiento: Optional[int] = None,
        anio_nacimiento: Optional[int] = None,
        nivel: Optional[str] = None,
        curso: Optional[int] = None,
        id_colegio: Optional[int] = None
    ):
        query = self.get_base_query()

        if search:
            query = query.filter(
                or_(
                    PersonaModel.nombres.ilike(f"%{search}%"),
                    PersonaModel.paterno.ilike(f"%{search}%"),
                    PersonaModel.materno.ilike(f"%{search}%"),
                    EstudianteModel.correo.ilike(f"%{search}%")
                )
            )
        if carnet:
            query = query.filter(EstudianteModel.carnet_identidad == carnet)
        if telefono:
            query = query.filter(EstudianteModel.telefono == telefono)
        if rude:
            query = query.filter(EstudianteModel.rude == rude)
        if mes_nacimiento:
            query = query.filter(extract('month', EstudianteModel.fecha_nacimiento) == mes_nacimiento)
        if anio_nacimiento:
            query = query.filter(extract('year', EstudianteModel.fecha_nacimiento) == anio_nacimiento)
        if nivel:
            query = query.filter(EstudianteModel.nivel == nivel)
        if curso:
            query = query.filter(EstudianteModel.curso == curso)
        if id_colegio:
            query = query.filter(EstudianteModel.id_colegio == id_colegio)

        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def update(self):
        self.db.commit()