from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.modules.personas.persona_model import (
    ColaboradorModel,
    DirectorModel,
    EstudianteModel,
    PersonaModel,
)
from app.modules.personas.persona_repository import PersonaRepository
from app.modules.personas.persona_schema import (
    ColaboradorCreateDTO,
    DirectorCreateDTO,
    EstudianteCreateDTO,
)


class PersonaService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = PersonaRepository(db)

    def list_estudiantes(self, page: int, limit: int):
        skip = (page - 1) * limit
        rows = self.repository.list_estudiantes(skip=skip, limit=limit)
        total = self.repository.count_estudiantes()
        items = [
            {
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
            for estudiante, persona in rows
        ]
        return items, total

    def list_directores(self, page: int, limit: int):
        skip = (page - 1) * limit
        rows = self.repository.list_directores(skip=skip, limit=limit)
        total = self.repository.count_directores()
        items = [
            {
                "id_director": director.id_director,
                "nombres": persona.nombres,
                "paterno": persona.paterno,
                "materno": persona.materno,
                "id_colegio": director.id_colegio,
                "telefono_1": director.telefono_1,
                "telefono_2": director.telefono_2,
            }
            for director, persona in rows
        ]
        return items, total

    def list_colaboradores(self, page: int, limit: int):
        skip = (page - 1) * limit
        rows = self.repository.list_colaboradores(skip=skip, limit=limit)
        total = self.repository.count_colaboradores()
        items = [
            {
                "id_colaborador": colaborador.id_colaborador,
                "nombres": persona.nombres,
                "paterno": persona.paterno,
                "materno": persona.materno,
                "presentacion": colaborador.presentacion,
                "rol": colaborador.rol,
                "tipo": colaborador.tipo,
                "correo": colaborador.correo,
            }
            for colaborador, persona in rows
        ]
        return items, total

    def get_personal_by_tipo(self, tipo: str, page: int, limit: int):
        skip = (page - 1) * limit
        if tipo == "DIRECTOR":
            rows = self.repository.list_directores(skip=skip, limit=limit)
            total = self.repository.count_directores()
            items = [
                {
                    "id_director": director.id_director,
                    "nombres": persona.nombres,
                    "paterno": persona.paterno,
                    "materno": persona.materno,
                    "id_colegio": director.id_colegio,
                    "telefono_1": director.telefono_1,
                    "telefono_2": director.telefono_2,
                }
                for director, persona in rows
            ]
            return items, total

        rows = self.repository.list_colaboradores_by_tipo(tipo, skip=skip, limit=limit)
        total = self.repository.count_colaboradores_by_tipo(tipo)
        items = [
            {
                "id_colaborador": colaborador.id_colaborador,
                "nombres": persona.nombres,
                "paterno": persona.paterno,
                "materno": persona.materno,
                "presentacion": colaborador.presentacion,
                "rol": colaborador.rol,
                "tipo": colaborador.tipo,
                "correo": colaborador.correo,
            }
            for colaborador, persona in rows
        ]
        return items, total

    def create_estudiante(self, data: EstudianteCreateDTO):
        with self.db.begin():
            persona = PersonaModel(nombres=data.nombres, paterno=data.paterno, materno=data.materno)
            self.repository.create_persona(persona)
            estudiante = EstudianteModel(
                id_estudiante=persona.id_persona,
                id_colegio=data.id_colegio,
                carnet_identidad=data.carnet_identidad,
                curso=data.curso,
                nivel=data.nivel,
                fecha_nacimiento=data.fecha_nacimiento,
                rude=data.rude,
                telefono=data.telefono,
                correo=data.correo,
            )
            self.repository.create_estudiante(estudiante)

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

    def create_director(self, data: DirectorCreateDTO):
        with self.db.begin():
            persona = PersonaModel(nombres=data.nombres, paterno=data.paterno, materno=data.materno)
            self.repository.create_persona(persona)
            director = DirectorModel(
                id_director=persona.id_persona,
                id_colegio=data.id_colegio,
                telefono_1=data.telefono_1,
                telefono_2=data.telefono_2,
            )
            self.repository.create_director(director)

        return {
            "id_director": director.id_director,
            "nombres": persona.nombres,
            "paterno": persona.paterno,
            "materno": persona.materno,
            "id_colegio": director.id_colegio,
            "telefono_1": director.telefono_1,
            "telefono_2": director.telefono_2,
        }

    def create_colaborador(self, data: ColaboradorCreateDTO):
        with self.db.begin():
            persona = PersonaModel(nombres=data.nombres, paterno=data.paterno, materno=data.materno)
            self.repository.create_persona(persona)
            colaborador = ColaboradorModel(
                id_colaborador=persona.id_persona,
                presentacion=data.presentacion,
                rol=data.rol,
                tipo=data.tipo,
                correo=data.correo,
            )
            self.repository.create_colaborador(colaborador)

        return {
            "id_colaborador": colaborador.id_colaborador,
            "nombres": persona.nombres,
            "paterno": persona.paterno,
            "materno": persona.materno,
            "presentacion": colaborador.presentacion,
            "rol": colaborador.rol,
            "tipo": colaborador.tipo,
            "correo": colaborador.correo,
        }

    def get_persona(self, persona_id: int):
        persona = self.repository.get_persona_by_id(persona_id)
        if not persona:
            raise NotFoundError("Persona no encontrada")
        return persona
