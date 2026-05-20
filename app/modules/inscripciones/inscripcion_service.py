from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.modules.colegios.colegio_model import ColegioModel
from app.modules.inscripciones.inscripcion_model import InscripcionModel
from app.modules.inscripciones.inscripcion_repository import InscripcionRepository
from app.modules.inscripciones.inscripcion_schema import InscripcionFormularioDTO
from app.modules.personas.persona_model import EstudianteModel, PersonaModel


class InscripcionService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = InscripcionRepository(db)

    def list_all(self, page: int, limit: int):
        skip = (page - 1) * limit
        return self.repository.list_all(skip=skip, limit=limit), self.repository.count_all()

    def registrar_formulario(self, data: InscripcionFormularioDTO):
        try:
            convocatoria = self.repository.get_convocatoria(data.id_convocatoria)
            if not convocatoria:
                raise NotFoundError("Convocatoria no encontrada")

            categoria = self.repository.get_categoria(data.id_categoria)
            if not categoria:
                raise NotFoundError("Categoria no encontrada")
            if categoria.id_convocatoria != data.id_convocatoria:
                raise BusinessRuleError("La categoria no pertenece a la convocatoria")

            colegio = self._obtener_o_crear_colegio(data)
            estudiante, persona = self._obtener_o_crear_estudiante(data, colegio.id_colegio)

            existente = self.repository.get_inscripcion_existente(estudiante.id_estudiante, data.id_convocatoria)
            if existente:
                raise ConflictError("El estudiante ya esta inscrito en esta convocatoria")

            inscripcion = InscripcionModel(
                id_estudiante=estudiante.id_estudiante,
                id_convocatoria=data.id_convocatoria,
                id_categoria=data.id_categoria,
                estado="PENDIENTE",
            )
            self.repository.create_inscripcion(inscripcion)
            self.db.commit()
            self.db.refresh(inscripcion)
            self.db.refresh(estudiante)
            self.db.refresh(persona)
            self.db.refresh(colegio)

            return {
                "inscripcion": inscripcion,
                "estudiante": self._estudiante_response(estudiante, persona),
                "colegio": self._colegio_response(colegio),
            }
        except (BusinessRuleError, ConflictError, NotFoundError):
            self.db.rollback()
            raise
        except IntegrityError as exc:
            self.db.rollback()
            message = str(exc.orig)
            if "estado REVISADO" in message:
                raise BusinessRuleError("El colegio debe estar REVISADO antes de confirmar la inscripcion") from exc
            raise ConflictError("No se pudo registrar la inscripcion") from exc
        except Exception:
            self.db.rollback()
            raise

    def _obtener_o_crear_colegio(self, data: InscripcionFormularioDTO):
        if data.id_colegio is not None and data.colegio_nuevo is not None:
            raise BusinessRuleError("Use id_colegio o colegio_nuevo, no ambos")

        if data.id_colegio is not None:
            colegio = self.repository.get_colegio(data.id_colegio)
            if not colegio:
                raise NotFoundError("Colegio no encontrado")
            return colegio

        if data.colegio_nuevo is None:
            raise BusinessRuleError("Debe indicar colegio")

        existente = self.repository.get_colegio_by_codigo(data.colegio_nuevo.codigo)
        if existente:
            return existente

        colegio = ColegioModel(**data.colegio_nuevo.model_dump(), estado="PENDIENTE")
        return self.repository.create_colegio(colegio)

    def _obtener_o_crear_estudiante(self, data: InscripcionFormularioDTO, colegio_id: int):
        estudiante_data = data.estudiante
        row = self.repository.get_estudiante_by_ci(estudiante_data.carnet_identidad)
        if row:
            estudiante, persona = row
            if estudiante.fecha_nacimiento != estudiante_data.fecha_nacimiento:
                raise ConflictError("El carnet existe, pero la fecha de nacimiento no coincide")
            persona.nombres = estudiante_data.nombres
            persona.paterno = estudiante_data.paterno
            persona.materno = estudiante_data.materno
            estudiante.id_colegio = colegio_id
            estudiante.curso = estudiante_data.curso
            estudiante.nivel = estudiante_data.nivel
            estudiante.rude = estudiante_data.rude
            estudiante.telefono = estudiante_data.telefono
            estudiante.correo = estudiante_data.correo
            self.db.flush()
            return estudiante, persona

        persona = PersonaModel(
            nombres=estudiante_data.nombres,
            paterno=estudiante_data.paterno,
            materno=estudiante_data.materno,
        )
        self.repository.create_persona(persona)
        estudiante = EstudianteModel(
            id_estudiante=persona.id_persona,
            id_colegio=colegio_id,
            carnet_identidad=estudiante_data.carnet_identidad,
            curso=estudiante_data.curso,
            nivel=estudiante_data.nivel,
            fecha_nacimiento=estudiante_data.fecha_nacimiento,
            rude=estudiante_data.rude,
            telefono=estudiante_data.telefono,
            correo=estudiante_data.correo,
        )
        self.repository.create_estudiante(estudiante)
        return estudiante, persona

    def _estudiante_response(self, estudiante, persona):
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

    def _colegio_response(self, colegio):
        return {
            "id_colegio": colegio.id_colegio,
            "codigo": colegio.codigo,
            "nombre": colegio.nombre,
            "tipo": colegio.tipo,
            "turno": colegio.turno,
            "departamento": colegio.departamento,
            "municipio": colegio.municipio,
            "calle": colegio.calle,
            "numero": colegio.numero,
            "estado": colegio.estado,
        }
