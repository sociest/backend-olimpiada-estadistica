from datetime import date

from sqlalchemy.orm import Session

from app.modules.personas.persona_model import EstudianteModel, PersonaModel


class EstudianteRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, estudiante_id: int):
        return (
            self.db.query(EstudianteModel, PersonaModel)
            .join(PersonaModel, EstudianteModel.id_estudiante == PersonaModel.id_persona)
            .filter(EstudianteModel.id_estudiante == estudiante_id)
            .first()
        )

    def get_by_documento_fecha(self, carnet_identidad: str, fecha_nacimiento: date):
        return (
            self.db.query(EstudianteModel, PersonaModel)
            .join(PersonaModel, EstudianteModel.id_estudiante == PersonaModel.id_persona)
            .filter(EstudianteModel.carnet_identidad == carnet_identidad)
            .filter(EstudianteModel.fecha_nacimiento == fecha_nacimiento)
            .first()
        )

    def get_model_by_id(self, estudiante_id: int):
        return self.db.query(EstudianteModel).filter(EstudianteModel.id_estudiante == estudiante_id).first()

    def get_persona_by_id(self, persona_id: int):
        return self.db.query(PersonaModel).filter(PersonaModel.id_persona == persona_id).first()

    def update(self):
        self.db.commit()
