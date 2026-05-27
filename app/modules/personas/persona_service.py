from sqlalchemy.orm import Session
from fastapi import UploadFile
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
    ColaboradorUpdateDTO,
    DirectorCreateDTO,
    EstudianteCreateDTO,
    DirectorUpdateDTO
)
from app.core.supabase_storage import SupabaseStorageClient
from app.core.exceptions import BusinessRuleError

class PersonaService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = PersonaRepository(db)
        self.storage = SupabaseStorageClient()

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
                "estado": persona.estado,
                "id_colegio": director.id_colegio,
                "telefono_1": director.telefono_1,
                "telefono_2": director.telefono_2,
            }
            for director, persona in rows
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
                    "estado": persona.estado,
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
        try:
            persona = PersonaModel(
                nombres=data.nombres,
                paterno=data.paterno,
                materno=data.materno
            )
            self.repository.create_persona(persona)  # hace self.db.add(persona)
            
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
            
            self.db.commit()   # ← commit explícito
            
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
        except Exception:
            self.db.rollback()   # ← rollback si algo falla
            raise

    def create_director(self, data: DirectorCreateDTO):
        try:
            persona = PersonaModel(
                nombres=data.nombres,
                paterno=data.paterno,
                materno=data.materno
            )
            self.repository.create_persona(persona)
            
            director = DirectorModel(
                id_director=persona.id_persona,
                id_colegio=data.id_colegio,
                telefono_1=data.telefono_1,
                telefono_2=data.telefono_2,
            )
            self.repository.create_director(director)
            
            self.db.commit()
            
            return {
                "id_director": director.id_director,
                "nombres": persona.nombres,
                "paterno": persona.paterno,
                "materno": persona.materno,
                "id_colegio": director.id_colegio,
                "telefono_1": director.telefono_1,
                "telefono_2": director.telefono_2,
            }
        except Exception:
            self.db.rollback()
            raise


    def get_colaborador_by_id(self, colaborador_id: int):
        colaborador = self.repository.get_colaborador_by_id(colaborador_id)
        if not colaborador:
            raise NotFoundError("Colaborador no encontrado")
        return colaborador

    def create_colaborador(self, data: ColaboradorCreateDTO, perfil_file: UploadFile = None):
        perfil_url = None
        if perfil_file:
            content = perfil_file.file.read()
            perfil_url = self.storage.upload_file(content, perfil_file.filename, "perfiles")

        persona = PersonaModel(nombres=data.nombres, paterno=data.paterno, materno=data.materno)
        colaborador = ColaboradorModel(
            perfil=perfil_url,
            presentacion=data.presentacion,
            rol=data.rol,
            tipo=data.tipo,
            correo=data.correo
        )
        return self.repository.create_colaborador(persona, colaborador)

    def update_colaborador(self, colaborador_id: int, data: ColaboradorUpdateDTO, perfil_file: UploadFile = None):
        colaborador = self.repository.get_colaborador_by_id(colaborador_id)
        if not colaborador:
            raise BusinessRuleError("Colaborador no encontrado")
        
        if perfil_file:
            if colaborador.perfil:
                self.storage.delete_file(colaborador.perfil)
            content = perfil_file.file.read()
            colaborador.perfil = self.storage.upload_file(content, perfil_file.filename, "perfiles")

        for key, value in data.model_dump(exclude_unset=True).items():
            if hasattr(colaborador, key):
                setattr(colaborador, key, value)
            elif hasattr(colaborador.persona, key):
                setattr(colaborador.persona, key, value)
        
        self.repository.update_colaborador()
        return colaborador

    def delete_logic(self, colaborador_id: int):
        colaborador = self.repository.get_colaborador_by_id(colaborador_id)
        colaborador.persona.estado = "INACTIVO"
        self.repository.update_colaborador()
        return colaborador

    def activate_logic(self, colaborador_id: int):
        colaborador = self.repository.get_colaborador_by_id(colaborador_id)
        colaborador.persona.estado = "ACTIVO"
        self.repository.update_colaborador()
        return colaborador

    def delete_physical(self, colaborador_id: int):
        colaborador = self.repository.get_colaborador_by_id(colaborador_id)
        if colaborador.perfil:
            self.storage.delete_file(colaborador.perfil)
        self.repository.delete_colaborador_physical(colaborador, colaborador.persona)

    def list_colaboradores(self, page, limit, nombre, correo, tipo, rol):
        skip = (page - 1) * limit
        items, total = self.repository.list_colaboradores_advanced(skip, limit, nombre, correo, tipo, rol)
        return [self._format_response(i) for i in items], total

    def _format_response(self, c: ColaboradorModel):
        return {
            "id_colaborador": c.id_colaborador,
            "nombres": c.nombres,
            "paterno": c.paterno,
            "materno": c.materno,
            "perfil": c.perfil,
            "presentacion": c.presentacion,
            "rol": c.rol,
            "tipo": c.tipo,
            "correo": c.correo,
            "estado": c.persona.estado
        }

    def get_persona(self, persona_id: int):
        persona = self.repository.get_persona_by_id(persona_id)
        if not persona:
            raise NotFoundError("Persona no encontrada")
        return persona

    def get_director_by_id(self, director_id: int):
        row = self.repository.get_director_by_id(director_id)
        if not row:
            raise NotFoundError("Director no encontrado")
        return row

    def update_director(self, director_id: int, data: DirectorUpdateDTO):
        director, persona = self.get_director_by_id(director_id)

        if data.nombres is not None: persona.nombres = data.nombres
        if data.paterno is not None: persona.paterno = data.paterno
        if data.materno is not None: persona.materno = data.materno
        
        if data.id_colegio is not None or "id_colegio" in data.model_dump(exclude_unset=True):
            director.id_colegio = data.id_colegio 
        if data.telefono_1 is not None: director.telefono_1 = data.telefono_1
        if data.telefono_2 is not None: director.telefono_2 = data.telefono_2

        self.repository.update_director(director, persona)
        return self._format_director_response(director, persona)

    def delete_director_logic(self, director_id: int):
        director, persona = self.get_director_by_id(director_id)
        persona.estado = "INACTIVO" 
        self.repository.update_director(director, persona)
        return self._format_director_response(director, persona)

    def delete_director_total(self, director_id: int):
        director, persona = self.get_director_by_id(director_id)
        self.repository.delete_director_total(director, persona)

    def alta_director_logic(self, director_id: int):
        director, persona = self.get_director_by_id(director_id)
        persona.estado = "ACTIVO"
        self.repository.update_director(director, persona)
        return self._format_director_response(director, persona)

    def list_directores_minified(self):
        rows = self.repository.list_directores_minified()
        return [
            {
                "id_director": row.id_persona,
                "nombres_completos": f"{row.nombres} {row.paterno} {row.materno or ''}".strip()
            }
            for row in rows
        ]

    def _format_director_response(self, director, persona):
        return {
            "id_director": director.id_director,
            "nombres": persona.nombres,
            "paterno": persona.paterno,
            "materno": persona.materno,
            "estado": persona.estado,
            "id_colegio": director.id_colegio,
            "telefono_1": director.telefono_1,
            "telefono_2": director.telefono_2,
        }
