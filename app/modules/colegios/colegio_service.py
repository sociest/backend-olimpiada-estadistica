from sqlalchemy.orm import Session
import asyncio
from app.core.exceptions import NotFoundError
from app.modules.colegios.colegio_model import ColegioModel, EstadoColegio
from app.modules.colegios.colegio_repository import ColegioRepository
from app.modules.colegios.colegio_schema import ColegioCreateDTO, ColegioUpdateDTO, CSVImportErrorDTO
from app.modules.colegios.csv.parser import parse_csv_colegios
from app.modules.personas.persona_model import DirectorModel,PersonaModel
from app.modules.personas.persona_repository import PersonaRepository
from app.modules.colegios.colegio_schema import CSVImportErrorDTO, ColegioCSVImportDTO
from app.modules.sistema.sistema_model import AuditoriaModel, TipoAccion, TipoModulo
from app.modules.sistema.sistema_repository import SistemaRepository

class ColegioService:
    def __init__(self, db: Session):
        self.repository = ColegioRepository(db)
        self.persona_repository = PersonaRepository(db)
        self.sistema_repository = SistemaRepository(db)

    def get_by_id(self, colegio_id: int):
        colegio = self.repository.get_by_id(colegio_id)
        if not colegio:
            raise NotFoundError("Colegio no encontrado")
        return colegio

    def get_all(self, page: int, limit: int, filters: dict = None):
        skip = (page - 1) * limit
        items, total = self.repository.get_all_filtered(skip=skip, limit=limit, filters=filters or {})
        return items, total
    
    def create(self, data: ColegioCreateDTO, current_admin_id: int):
        colegio_data = data.model_dump(exclude_unset=True)
        if 'estado' not in colegio_data:
            colegio_data['estado'] = EstadoColegio.REVISADO
        colegio = ColegioModel(**colegio_data)
        created = self.repository.create(colegio)
        self._auditar(
            current_admin_id,
            TipoAccion.CREAR,
            f"Colegio creado {created.nombre} codigo {created.codigo}",
        )
        return created

    def update(self, colegio_id: int, data: ColegioUpdateDTO, current_admin_id: int):
        colegio = self.get_by_id(colegio_id)
        updates = data.model_dump(exclude_unset=True)
        for key, value in updates.items():
            setattr(colegio, key, value)
        updated = self.repository.update(colegio)
        self._auditar(
            current_admin_id,
            TipoAccion.ACTUALIZAR,
            f"Colegio actualizado {updated.nombre} codigo {updated.codigo}",
        )
        return updated
    
    def delete_logic(self, colegio_id: int, current_admin_id: int):
        colegio = self.get_by_id(colegio_id)
        updated = self.repository.update_estado(colegio, EstadoColegio.INACTIVO)
        self._auditar(
            current_admin_id,
            TipoAccion.ACTUALIZAR,
            f"Colegio {updated.nombre} codigo {updated.codigo} dado de baja",
        )
        return updated

    def alta_logic(self, colegio_id: int, current_admin_id: int):
        colegio = self.get_by_id(colegio_id)
        updated = self.repository.update_estado(colegio, EstadoColegio.REVISADO)
        self._auditar(
            current_admin_id,
            TipoAccion.ACTUALIZAR,
            f"Colegio {updated.nombre} codigo {updated.codigo} dado de alta",
        )
        return updated

    def delete_total(self, colegio_id: int, current_admin_id: int):
        colegio = self.get_by_id(colegio_id)
        descripcion = f"Colegio eliminado {colegio.nombre} codigo {colegio.codigo}"
        self.repository.delete_physical(colegio)
        self._auditar(current_admin_id, TipoAccion.ELIMINAR, descripcion)

    def parse_csv_file(self, file, departamento: str):
        return parse_csv_colegios( file=file, departamento=departamento)

    def import_from_csv(self, colegios: list[ColegioCSVImportDTO], current_admin_id: int):

        insertados = 0
        errores = []
        codigos_csv = set()

        for index, colegio_data in enumerate(colegios):
            fila = index + 1
            try:
                if colegio_data.codigo in codigos_csv:
                    errores.append(
                        CSVImportErrorDTO(
                            fila=fila,
                            codigo=str(
                                colegio_data.codigo
                            ),
                            nombre=colegio_data.nombre,
                            error="Código duplicado en CSV"
                        )
                    )
                    continue

                codigos_csv.add(colegio_data.codigo)
                
                if self.repository.exists_by_codigo(colegio_data.codigo):
                    errores.append(
                        CSVImportErrorDTO(
                            fila=fila,
                            codigo=str(
                                colegio_data.codigo
                            ),
                            nombre=colegio_data.nombre,
                            error="Código ya existe en base de datos"
                        )
                    )
                    continue

                colegio = ColegioModel(
                    **colegio_data.model_dump(
                        exclude={"directores"}
                    )
                )

                self.repository.create_no_commit(
                    colegio
                )

                for director_data in colegio_data.directores:
                    persona = PersonaModel(
                        nombres=director_data.nombres,
                        paterno=director_data.paterno,
                        materno=director_data.materno
                    )

                    self.persona_repository.create_persona(
                        persona
                    )

                    director = DirectorModel(
                        id_director=persona.id_persona,
                        id_colegio=colegio.id_colegio,
                        telefono_1=director_data.telefono_1,
                        telefono_2=director_data.telefono_2
                    )

                    self.persona_repository.create_director(
                        director
                    )

                insertados += 1

            except Exception as e:
                self.repository.rollback()
                errores.append(
                    CSVImportErrorDTO(
                        fila=fila,
                        codigo=str(
                            colegio_data.codigo
                        ),
                        nombre=colegio_data.nombre,
                        error=str(e)
                    )
                )

        self.repository.commit()
        if insertados > 0:
            self._auditar(
                current_admin_id,
                TipoAccion.CREAR,
                f"Importacion CSV de colegios completada con {insertados} colegios insertados",
            )

        return {
            "insertados": insertados,
            "errores": errores
        }
    
    def get_all_minified(self):
        return self.repository.get_all_minified()

    def _auditar(self, current_admin_id: int, accion: TipoAccion, descripcion: str):
        self.sistema_repository.create_auditoria(
            AuditoriaModel(
                id_administrador=current_admin_id,
                accion=accion,
                modulo=TipoModulo.COLEGIO,
                descripcion=descripcion,
            )
        )

    async def get_colegios_minified(self):
        try:
            items = await asyncio.to_thread(self.repository.get_all_minified)
        except Exception:
            return []

        return [
            {
                "id_colegio": item.id_colegio,
                "nombre": item.nombre,
                "municipio": item.municipio,
                "turno": item.turno
            }
            for item in items or []
        ]