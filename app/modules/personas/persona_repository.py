from sqlalchemy.orm import Session

from app.modules.personas.persona_model import (
    ColaboradorModel,
    DirectorModel,
    EstudianteModel,
    PersonaModel,
)


class PersonaRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_persona_by_id(self, persona_id: int):
        return self.db.query(PersonaModel).filter(PersonaModel.id_persona == persona_id).first()

    def create_persona(self, persona: PersonaModel):
        self.db.add(persona)
        self.db.flush()
        return persona

    def create_estudiante(self, estudiante: EstudianteModel):
        self.db.add(estudiante)
        return estudiante

    def create_director(self, director: DirectorModel):
        self.db.add(director)
        return director

    def create_colaborador(self, colaborador: ColaboradorModel):
        self.db.add(colaborador)
        return colaborador

    def list_estudiantes(self, skip: int, limit: int):
        return (
            self.db.query(EstudianteModel, PersonaModel)
            .join(PersonaModel, EstudianteModel.id_estudiante == PersonaModel.id_persona)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_estudiantes(self):
        return self.db.query(EstudianteModel).count()

    def list_directores(self, skip: int, limit: int):
        return (
            self.db.query(DirectorModel, PersonaModel)
            .join(PersonaModel, DirectorModel.id_director == PersonaModel.id_persona)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_directores(self):
        return self.db.query(DirectorModel).count()

    def list_colaboradores(self, skip: int, limit: int):
        return (
            self.db.query(ColaboradorModel, PersonaModel)
            .join(PersonaModel, ColaboradorModel.id_colaborador == PersonaModel.id_persona)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_colaboradores_by_tipo(self, tipo: str, skip: int, limit: int):
        return (
            self.db.query(ColaboradorModel, PersonaModel)
            .join(PersonaModel, ColaboradorModel.id_colaborador == PersonaModel.id_persona)
            .filter(ColaboradorModel.tipo == tipo)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_colaboradores_by_tipo(self, tipo: str):
        return self.db.query(ColaboradorModel).filter(ColaboradorModel.tipo == tipo).count()

    def count_colaboradores(self):
        return self.db.query(ColaboradorModel).count()
    
    def get_director_by_id(self, director_id: int):
        return self.db.query(DirectorModel, PersonaModel)\
            .join(PersonaModel, DirectorModel.id_director == PersonaModel.id_persona)\
            .filter(DirectorModel.id_director == director_id).first()

    def update_director(self, director: DirectorModel, persona: PersonaModel):
        self.db.commit()
        self.db.refresh(director)
        self.db.refresh(persona)
        return director, persona

    def delete_director_total(self, director: DirectorModel, persona: PersonaModel):
        self.db.delete(director)
        self.db.delete(persona)
        self.db.commit()

    def list_directores_minified(self):
        return self.db.query(PersonaModel.id_persona, PersonaModel.nombres, PersonaModel.paterno, PersonaModel.materno)\
            .join(DirectorModel, DirectorModel.id_director == PersonaModel.id_persona)\
            .filter(PersonaModel.estado == "ACTIVO").all()
