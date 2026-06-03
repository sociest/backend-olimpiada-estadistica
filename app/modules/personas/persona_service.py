from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.core.exceptions import NotFoundError
from app.modules.personas.persona_model import (
    ColaboradorModel,
    DirectorModel,
    EstadoPersona,
    PersonaModel,
    TipoColaborador,
)
from app.modules.personas.persona_repository import PersonaRepository
from app.modules.personas.persona_schema import (
    ColaboradorCreateDTO,
    ColaboradorUpdateDTO,
    DirectorCreateDTO,
    DirectorUpdateDTO
)
from app.core.supabase_storage import SupabaseStorageClient
from app.core.exceptions import BusinessRuleError
from app.modules.sistema.sistema_model import AuditoriaModel, TipoAccion, TipoModulo
from app.modules.sistema.sistema_repository import SistemaRepository

class PersonaService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = PersonaRepository(db)
        self.storage = SupabaseStorageClient()
        self.sistema_repository = SistemaRepository(db)
    
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


    def get_personal_by_tipo(self, tipo: TipoColaborador | str, page: int, limit: int):
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
                    "telefono_2": director.telefono_2
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
                "estado": persona.estado,
                "perfil": colaborador.perfil
            }
            for colaborador, persona in rows
        ]
        return items, total

    def get_colaboradores_activos_by_tipo(self, tipo: TipoColaborador, page: int, limit: int):
        skip = (page - 1) * limit
        rows = self.repository.list_colaboradores_activos_by_tipo(tipo, skip=skip, limit=limit)
        total = self.repository.count_colaboradores_activos_by_tipo(tipo)
        items = [
            {
                "nombres": persona.nombres,
                "paterno": persona.paterno,
                "materno": persona.materno,
                "presentacion": colaborador.presentacion,
                "rol": colaborador.rol,
                "correo": colaborador.correo,
                "perfil": colaborador.perfil
            } 
            for colaborador, persona in rows
        ]
        return items, total
    
    def create_director(self, data: DirectorCreateDTO, current_admin_id: int):
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
            self._auditar(
                current_admin_id,
                TipoAccion.CREAR,
                TipoModulo.DIRECTOR,
                f"Director creado {persona.nombres} {persona.paterno}",
            )
            
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

    def update_director(self, director_id: int, data: DirectorUpdateDTO, current_admin_id: int):
        director, persona = self.get_director_by_id(director_id)

        if data.nombres is not None: persona.nombres = data.nombres
        if data.paterno is not None: persona.paterno = data.paterno
        if data.materno is not None: persona.materno = data.materno
        
        if data.id_colegio is not None or "id_colegio" in data.model_dump(exclude_unset=True):
            director.id_colegio = data.id_colegio 
        if data.telefono_1 is not None: director.telefono_1 = data.telefono_1
        if data.telefono_2 is not None: director.telefono_2 = data.telefono_2

        self.repository.update_director(director, persona)
        self._auditar(
            current_admin_id,
            TipoAccion.ACTUALIZAR,
            TipoModulo.DIRECTOR,
            f"Director actualizado {persona.nombres} {persona.paterno}",
        )
        return self._format_director_response(director, persona)

    def delete_director_logic(self, director_id: int, current_admin_id: int):
        director, persona = self.get_director_by_id(director_id)
        persona.estado = EstadoPersona.INACTIVO 
        self.repository.update_director(director, persona)
        self._auditar(
            current_admin_id,
            TipoAccion.ACTUALIZAR,
            TipoModulo.DIRECTOR,
            f"Director dado de baja {persona.nombres} {persona.paterno}",
        )
        return self._format_director_response(director, persona)

    def delete_director_total(self, director_id: int, current_admin_id: int):
        director, persona = self.get_director_by_id(director_id)
        descripcion = f"Director eliminado {persona.nombres} {persona.paterno}"
        self.repository.delete_director_total(director, persona)
        self._auditar(current_admin_id, TipoAccion.ELIMINAR, TipoModulo.DIRECTOR, descripcion)

    def alta_director_logic(self, director_id: int, current_admin_id: int):
        director, persona = self.get_director_by_id(director_id)
        persona.estado = EstadoPersona.ACTIVO
        self.repository.update_director(director, persona)
        self._auditar(
            current_admin_id,
            TipoAccion.ACTUALIZAR,
            TipoModulo.DIRECTOR,
            f"Director dado de alta {persona.nombres} {persona.paterno}",
        )
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
    
    def create_colaborador(self, data: ColaboradorCreateDTO, perfil_file: UploadFile | None = None, current_admin_id: int | None = None):
        perfil_url = None
        if perfil_file:
            content = perfil_file.file.read()
            perfil_url = self.storage.upload_material(content, perfil_file.filename, content_type=perfil_file.content_type)

        persona = PersonaModel(
            nombres=data.nombres,
            paterno=data.paterno,
            materno=data.materno
        )
        colaborador = ColaboradorModel(
            perfil=perfil_url,
            presentacion=data.presentacion,
            rol=data.rol,
            tipo=data.tipo,
            correo=data.correo
        )
        created = self.repository.create_colaborador(persona, colaborador)
        if current_admin_id is not None:
            self._auditar(
                current_admin_id,
                TipoAccion.CREAR,
                TipoModulo.COLABORADOR,
                f"Colaborador creado {persona.nombres} {persona.paterno} tipo {colaborador.tipo}",
            )
        return created

    def update_colaborador(self, colaborador_id: int, data: ColaboradorUpdateDTO, perfil_file: UploadFile | None = None, current_admin_id: int | None = None):
        colaborador = self.repository.get_colaborador_by_id(colaborador_id)
        if not colaborador:
            raise BusinessRuleError("Colaborador no encontrado")
        
        if perfil_file:
            if colaborador.perfil:
                self.storage.delete_file(colaborador.perfil)
            content = perfil_file.file.read()
            colaborador.perfil = self.storage.upload_material(content, perfil_file.filename, content_type=perfil_file.content_type)

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(colaborador, key):
                setattr(colaborador, key, value)
            elif hasattr(colaborador.persona, key):
                setattr(colaborador.persona, key, value)
        
        self.repository.update_colaborador()
        if current_admin_id is not None:
            self._auditar(
                current_admin_id,
                TipoAccion.ACTUALIZAR,
                TipoModulo.COLABORADOR,
                f"Colaborador actualizado {colaborador.persona.nombres} {colaborador.persona.paterno} tipo {colaborador.tipo}",
            )
        return colaborador

    def delete_logic(self, colaborador_id: int, current_admin_id: int | None = None):
        colaborador = self.repository.get_colaborador_by_id(colaborador_id)
        if not colaborador:
            raise BusinessRuleError("Colaborador no encontrado")
        colaborador.persona.estado = EstadoPersona.INACTIVO
        self.repository.update_colaborador()
        if current_admin_id is not None:
            self._auditar(
                current_admin_id,
                TipoAccion.ACTUALIZAR,
                TipoModulo.COLABORADOR,
                f"Colaborador dado de baja {colaborador.persona.nombres} {colaborador.persona.paterno}",
            )
        return colaborador

    def activate_logic(self, colaborador_id: int, current_admin_id: int | None = None):
        colaborador = self.repository.get_colaborador_by_id(colaborador_id)
        if not colaborador:
            raise BusinessRuleError("Colaborador no encontrado")
        colaborador.persona.estado = EstadoPersona.ACTIVO
        self.repository.update_colaborador()
        if current_admin_id is not None:
            self._auditar(
                current_admin_id,
                TipoAccion.ACTUALIZAR,
                TipoModulo.COLABORADOR,
                f"Colaborador dado de alta {colaborador.persona.nombres} {colaborador.persona.paterno}",
            )
        return colaborador

    def delete_physical(self, colaborador_id: int, current_admin_id: int | None = None):
        colaborador = self.repository.get_colaborador_by_id(colaborador_id)
        if not colaborador:
            raise BusinessRuleError("Colaborador no encontrado")
        if colaborador.perfil:
            self.storage.delete_file(colaborador.perfil)
        descripcion = f"Colaborador eliminado {colaborador.persona.nombres} {colaborador.persona.paterno}"
        self.repository.delete_colaborador_physical(colaborador, colaborador.persona)
        if current_admin_id is not None:
            self._auditar(current_admin_id, TipoAccion.ELIMINAR, TipoModulo.COLABORADOR, descripcion)

    def get_colaborador_by_id(self, colaborador_id: int):
        colaborador = self.repository.get_colaborador_by_id(colaborador_id)
        if not colaborador:
            raise BusinessRuleError("Colaborador no encontrado")
        return colaborador

    def list_colaboradores(self, page: int, limit: int, nombre: str | None, correo: str | None, tipo: TipoColaborador | None, rol: str | None, estado: EstadoPersona | None):
        skip = (page - 1) * limit
        items, total = self.repository.list_colaboradores_advanced(skip, limit, nombre, correo, tipo, rol, estado)
        return [self._format_response(i) for i in items], total

    def _format_response(self, c: ColaboradorModel):
        return {
            "id_colaborador": c.id_colaborador,
            "nombres": c.persona.nombres if c.persona else "",
            "paterno": c.persona.paterno if c.persona else "",
            "materno": c.persona.materno if c.persona else "",
            "perfil": c.perfil,
            "presentacion": c.presentacion,
            "rol": c.rol,
            "tipo": c.tipo,
            "correo": c.correo,
            "estado": c.persona.estado if c.persona else EstadoPersona.ACTIVO
        }

    def _auditar(self, current_admin_id: int, accion: TipoAccion, modulo: TipoModulo, descripcion: str):
        self.sistema_repository.create_auditoria(
            AuditoriaModel(
                id_administrador=current_admin_id,
                accion=accion,
                modulo=modulo,
                descripcion=descripcion,
            )
        )
