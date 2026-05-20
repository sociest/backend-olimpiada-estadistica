from datetime import date

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.modules.estudiantes.estudiante_repository import EstudianteRepository
from app.modules.estudiantes.estudiante_schema import EstudianteUpdateDTO


class EstudianteService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = EstudianteRepository(db)

    def buscar_por_documento_fecha(self, carnet_identidad: str, fecha_nacimiento: date):
        row = self.repository.get_by_documento_fecha(carnet_identidad, fecha_nacimiento)
        if not row:
            raise NotFoundError("Estudiante no encontrado")
        estudiante, persona = row
        return self._to_response(estudiante, persona)

    def update(self, estudiante_id: int, data: EstudianteUpdateDTO):
        estudiante = self.repository.get_model_by_id(estudiante_id)
        persona = self.repository.get_persona_by_id(estudiante_id)
        if not estudiante or not persona:
            raise NotFoundError("Estudiante no encontrado")

        updates = data.model_dump(exclude_unset=True)
        for field in ("nombres", "paterno", "materno"):
            if field in updates:
                setattr(persona, field, updates[field])
        for field in ("id_colegio", "curso", "nivel", "rude", "telefono", "correo"):
            if field in updates:
                setattr(estudiante, field, updates[field])

        self.repository.update()
        self.db.refresh(estudiante)
        self.db.refresh(persona)
        return self._to_response(estudiante, persona)

    def _to_response(self, estudiante, persona):
        return {
            "id_estudiante": estudiante.id_estudiante,
            "nombres": persona.nombres,
            "paterno": persona.paterno,
            "materno": persona.materno,
            "id_colegio": estudiante.id_colegio,
            "carnet_identidad": estudiante.carnet_identidad,
            "curso": estudiante.curso,
            "nivel": estudiante.nivel,
            "fecha_nacimiento": estudiante.fecha_nacimiento,
            "rude": estudiante.rude,
            "telefono": estudiante.telefono,
            "correo": estudiante.correo,
        }
