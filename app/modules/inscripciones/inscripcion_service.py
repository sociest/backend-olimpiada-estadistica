from datetime import date, datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.modules.inscripciones.inscripcion_model import InscripcionModel
from app.modules.inscripciones.inscripcion_repository import InscripcionRepository
from app.modules.inscripciones.inscripcion_schema import InscripcionFormularioDTO, InscripcionAdminCreateDTO, InscripcionEstadoUpdateDTO
from app.modules.personas.persona_model import PersonaModel
from app.modules.estudiantes.estudiante_model import EstudianteModel
from typing import Optional
class InscripcionService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = InscripcionRepository(db)

    def _calcular_edad(self, fecha_nacimiento: date) -> int:
        today = date.today()
        return today.year - fecha_nacimiento.year - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

    def buscar_estudiante_registro(self, carnet_identidad: str, fecha_nacimiento: date):
        row = self.repository.get_estudiante_by_ci_fecha(carnet_identidad, fecha_nacimiento)
        if not row:
            raise NotFoundError("Estudiante no encontrado o datos de verificación incorrectos")
        
        estudiante, persona = row
        edad = self._calcular_edad(estudiante.fecha_nacimiento)
        
        response = {
            "id_estudiante": estudiante.id_estudiante,
            "nombres": persona.nombres,
            "paterno": persona.paterno,
            "materno": persona.materno,
            "carnet_identidad": estudiante.carnet_identidad,
            "fecha_nacimiento": estudiante.fecha_nacimiento,
            "curso": estudiante.curso,
            "nivel": estudiante.nivel,
            "rude": estudiante.rude,
            "telefono": estudiante.telefono,
            "correo": estudiante.correo,
            "id_colegio": estudiante.id_colegio,
            "ya_inscrito": False,
            "id_inscripcion": None,
            "restriccion_edad": None,
            "inactividad": False,
            "mensaje_inactividad": None
            
        }

        if edad > 21:
            response["restriccion_edad"] = "El estudiante supera la edad límite de participación (21 años)."
            return response
        if edad < 14:
            response["restriccion_edad"] = "El estudiante es menor a la edad mínima requerida (14 años)."
            return response

        inscripcion = self.db.query(InscripcionModel).filter(InscripcionModel.id_estudiante == estudiante.id_estudiante).first()
        if inscripcion:
            response["ya_inscrito"] = True
            response["id_inscripcion"] = inscripcion.id_inscripcion
        
        if persona.estado == "INACTIVO":
            response["mensaje_inactividad"] = "El estudiante tiene su cuenta inactiva."
            response["inactividad"] = True

        return response

    def registrar_formulario(self, data: InscripcionFormularioDTO):
        try:
            convocatoria = self.repository.get_convocatoria(data.id_convocatoria)
            if not convocatoria:
                raise NotFoundError("Convocatoria no encontrada")

            edad = self._calcular_edad(data.estudiante.fecha_nacimiento)
            if edad < 14 or edad > 21:
                raise BusinessRuleError("El estudiante no cumple con el rango de edad permitido (14-21 años)")

            categoria = self.repository.buscar_categoria_automatica(
                data.id_convocatoria, data.estudiante.curso, data.estudiante.nivel
            )
            if not categoria:
                raise BusinessRuleError("El curso y nivel ingresados no corresponden a ninguna de las categorias activas")

            colegio = self.repository.get_colegio(data.id_colegio)
            if not colegio:
                raise NotFoundError("Colegio no encontrado")

            estudiante, persona = self._obtener_o_crear_estudiante(data, colegio.id_colegio)

            existente = self.repository.get_inscripcion_existente(estudiante.id_estudiante, data.id_convocatoria)
            if existente:
                raise ConflictError("El estudiante ya esta inscrito en esta convocatoria")

            inscripcion = InscripcionModel(
                id_estudiante=estudiante.id_estudiante,
                id_convocatoria=data.id_convocatoria,
                id_categoria=categoria.id_categoria,
                estado="PENDIENTE",
            )
            self.repository.create_inscripcion(inscripcion)
            self.repository.commit()
            self.db.refresh(inscripcion)
            return {
                "inscripcion": inscripcion,
                "estudiante": self._estudiante_response(estudiante, persona),
                "colegio": self._colegio_response(colegio),
            }
        except Exception:
            self.db.rollback()
            raise

    def crear_inscripcion_admin(self, data: InscripcionAdminCreateDTO):
        estudiante = self.repository.get_estudiante_by_id(data.id_estudiante)
        if not estudiante:
            raise NotFoundError("Estudiante no registrado")

        edad = self._calcular_edad(estudiante.fecha_nacimiento)
        if edad < 14 or edad > 21:
            raise BusinessRuleError("El estudiante no cumple con el rango de edad institucional (14-21 años)")

        categoria = self.repository.get_categoria(data.id_categoria)
        if not categoria:
            raise NotFoundError("La categoria especificada no existe")

        if categoria.id_convocatoria != data.id_convocatoria:
            raise BusinessRuleError("La categoria seleccionada no corresponde a la convocatoria")

        existente = self.repository.get_inscripcion_existente(data.id_estudiante, data.id_convocatoria)
        if existente:
            raise ConflictError("Inscripción duplicada detectada para esta convocatoria")
        
        if estudiante.estado == "INACTIVO":
            raise BusinessRuleError("El estudiante tiene su cuenta inactiva")

        nueva_inscripcion = InscripcionModel(
            id_estudiante=data.id_estudiante,
            id_convocatoria=data.id_convocatoria,
            id_categoria=data.id_categoria,
            estado="PENDIENTE"
        )
        self.repository.create_inscripcion(nueva_inscripcion)
        self.repository.commit()
        self.db.refresh(nueva_inscripcion)
        return nueva_inscripcion

    def list_all(
        self, page: int, limit: int, id_colegio: Optional[int] = None, id_categoria: Optional[int] = None,
        estado: Optional[str] = None, search_nombre: Optional[str] = None, search_documento: Optional[str] = None,
        fecha_inicio: Optional[datetime] = None, fecha_fin: Optional[datetime] = None
    ):
        skip = (page - 1) * limit
        return self.repository.list_inscripciones_avanzado(
            skip, limit, id_colegio, id_categoria, estado, search_nombre, search_documento, fecha_inicio, fecha_fin
        )

    def obtener_por_id(self, inscripcion_id: int):
        inscripcion = self.repository.get_by_id(inscripcion_id)
        if not inscripcion:
            raise NotFoundError("Inscripción no encontrada")
        return inscripcion

    def actualizar_estado(self, inscripcion_id: int, data: InscripcionEstadoUpdateDTO):
        inscripcion = self.obtener_por_id(inscripcion_id)
        if data.estado not in ["APROBADO", "RECHAZADO", "PENDIENTE"]:
            raise BusinessRuleError("Estado de inscripcion invalido")
        inscripcion.estado = data.estado
        self.repository.commit()
        return inscripcion

    def eliminar_inscripcion(self, inscripcion_id: int):
        inscripcion = self.obtener_por_id(inscripcion_id)
        self.repository.delete(inscripcion)
        self.repository.commit()

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
            return estudiante, persona

        persona = PersonaModel(nombres=estudiante_data.nombres, paterno=estudiante_data.paterno, materno=estudiante_data.materno)
        self.repository.create_persona(persona)
        estudiante = EstudianteModel(
            id_estudiante=persona.id_persona, id_colegio=colegio_id, carnet_identidad=estudiante_data.carnet_identidad,
            curso=estudiante_data.curso, nivel=estudiante_data.nivel, fecha_nacimiento=estudiante_data.fecha_nacimiento,
            rude=estudiante_data.rude, telefono=estudiante_data.telefono, correo=estudiante_data.correo
        )
        self.repository.create_estudiante(estudiante)
        return estudiante, persona

    def _estudiante_response(self, estudiante, persona):
        return {
            "id_estudiante": estudiante.id_estudiante, "nombres": persona.nombres, "paterno": persona.paterno,
            "materno": persona.materno, "id_colegio": estudiante.id_colegio, "carnet_identidad": estudiante.carnet_identidad,
            "curso": estudiante.curso, "nivel": estudiante.nivel, "fecha_nacimiento": estudiante.fecha_nacimiento,
            "rude": estudiante.rude, "telefono": estudiante.telefono, "correo": estudiante.correo
        }

    def _colegio_response(self, colegio):
        return {"nombre": colegio.nombre, "tipo": colegio.tipo, "turno": colegio.turno, "calle": colegio.calle}