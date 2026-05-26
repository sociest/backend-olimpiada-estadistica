from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.modules.colegios.colegio_model import ColegioModel
from app.modules.colegios.colegio_repository import ColegioRepository
from app.modules.colegios.colegio_schema import ColegioCreateDTO, ColegioUpdateDTO, CSVImportErrorDTO
from app.modules.colegios.csv.parser import parse_csv_colegios
from app.modules.personas.persona_model import DirectorModel,PersonaModel
from app.modules.personas.persona_repository import PersonaRepository
from app.modules.colegios.colegio_schema import CSVImportErrorDTO, ColegioCSVImportDTO

class ColegioService:
    def __init__(self, db: Session):
        self.repository = ColegioRepository(db)
        self.persona_repository = PersonaRepository(db)

    def get_by_id(self, colegio_id: int):
        colegio = self.repository.get_by_id(colegio_id)
        if not colegio:
            raise NotFoundError("Colegio no encontrado")
        return colegio

    def get_all(self, page: int, limit: int, filters: dict = None):
        skip = (page - 1) * limit
        items, total = self.repository.get_all_filtered(skip=skip, limit=limit, filters=filters or {})
        return items, total
    
    def create(self, data: ColegioCreateDTO):
        colegio = ColegioModel(**data.model_dump())
        return self.repository.create(colegio)

    def update(self, colegio_id: int, data: ColegioUpdateDTO):
        colegio = self.get_by_id(colegio_id)
        updates = data.model_dump(exclude_unset=True)
        for key, value in updates.items():
            setattr(colegio, key, value)
        return self.repository.update(colegio)
    
    def delete_logic(self, colegio_id: int):
        colegio = self.get_by_id(colegio_id)
        return self.repository.update_estado(colegio, "INACTIVO")

    def delete_total(self, colegio_id: int):
        colegio = self.get_by_id(colegio_id)
        self.repository.delete_physical(colegio)

    def parse_csv_file(self, file, departamento: str):
        return parse_csv_colegios( file=file, departamento=departamento)

    def import_from_csv(self, colegios: list[ColegioCSVImportDTO]):

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

        return {
            "insertados": insertados,
            "errores": errores
        }
    
    def get_all_minified(self):
        return self.repository.get_all_minified()