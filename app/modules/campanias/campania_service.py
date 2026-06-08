from sqlalchemy.orm import Session
from app.core.exceptions import BusinessRuleError, NotFoundError
from app.modules.campanias.campania_model import CampaniaEmail, EstadoCampania, CampaniaDestinatario
from app.modules.campanias.campania_schema import CampaniaCreateDTO, CampaniaUpdateDTO
from app.modules.campanias.campania_repository import CampaniaRepository
from app.modules.sistema.sistema_model import AuditoriaModel, TipoAccion, TipoModulo
from app.modules.sistema.sistema_repository import SistemaRepository
from app.modules.estudiantes.estudiante_model import EstudianteModel

class CampaniaService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CampaniaRepository(db)
        self.sistema_repository = SistemaRepository(db)

    def listar_campanias(self, page: int, limit: int, **filters):
        skip = (page - 1) * limit
        items, total = self.repo.get_all(skip=skip, limit=limit, **filters)
        return items, total

    def obtener_por_id(self, id_campania: int):
        campania = self.repo.get_by_id(id_campania)
        if not campania:
            raise NotFoundError("Campaña no encontrada")
        return campania

    def crear_campania(self, data: CampaniaCreateDTO, current_admin_id: int) -> CampaniaEmail:
        dict_enlaces = [e.model_dump() for e in data.enlaces] if data.enlaces else []
        nueva = CampaniaEmail(
            nombre=data.nombre,
            asunto=data.asunto,
            contenido_mensaje=data.contenido_mensaje,
            contenido_secundario=data.contenido_secundario,
            enlaces=dict_enlaces,
            fecha_programada=data.fecha_programada,
            estado=EstadoCampania.BORRADOR
        )
        self.db.add(nueva)
        self.db.commit()
        self.db.refresh(nueva)

        if data.destinatarios_ids:
            self._gestionar_destinatarios(nueva.id_campania_email, agregar=data.destinatarios_ids)
        
        auditoria_registro = AuditoriaModel(
            id_administrador=current_admin_id,
            accion=TipoAccion.CREAR,
            modulo=TipoModulo.CAMPANIA,
            descripcion=f"Campaña creada {nueva.nombre} de asunto {nueva.asunto}"
        )
        self.sistema_repository.create_auditoria(auditoria_registro)
        
        return nueva

    def actualizar_campania(self, id_campania: int, data: CampaniaUpdateDTO, current_admin_id: int) -> CampaniaEmail:
        campania = self.obtener_por_id(id_campania)
        
        if campania.estado != EstadoCampania.BORRADOR:
            raise BusinessRuleError("Solo se pueden editar campañas en estado BORRADOR")

        if data.nombre: campania.nombre = data.nombre
        if data.asunto: campania.asunto = data.asunto
        if data.contenido_mensaje: campania.contenido_mensaje = data.contenido_mensaje
        if data.contenido_secundario: campania.contenido_secundario = data.contenido_secundario
        if data.enlaces is not None: campania.enlaces = [e.model_dump() for e in data.enlaces]
        if data.fecha_programada: campania.fecha_programada = data.fecha_programada

        if data.agregar_destinatarios or data.eliminar_destinatarios:
            self._gestionar_destinatarios(campania.id_campania_email, data.agregar_destinatarios, data.eliminar_destinatarios)

        self.db.commit()
        self.db.refresh(campania)
        auditoria_registro = AuditoriaModel(
            id_administrador=current_admin_id,
            accion=TipoAccion.ACTUALIZAR,
            modulo=TipoModulo.CAMPANIA,
            descripcion=f"Campaña actualizada {campania.nombre} de asunto {campania.asunto}"
        )
        self.sistema_repository.create_auditoria(auditoria_registro)
        return campania

    def cambiar_estado(self, id_campania: int, nuevo_estado: EstadoCampania, current_admin_id: int):
        campania = self.obtener_por_id(id_campania)

        if nuevo_estado == EstadoCampania.PROGRAMADA:
            if campania.estado not in (EstadoCampania.BORRADOR, EstadoCampania.CANCELADA):
                raise BusinessRuleError("Solo se puede programar desde BORRADOR o CANCELADA")
            total_dest = self.db.query(CampaniaDestinatario).filter_by(id_campania_email=id_campania).count()
            if total_dest == 0:
                raise BusinessRuleError("No se puede programar una campaña sin destinatarios")
                
        elif nuevo_estado == EstadoCampania.CANCELADA:
            if campania.estado not in (EstadoCampania.PROGRAMADA, EstadoCampania.EN_PROCESO):
                raise BusinessRuleError("Solo se puede cancelar una campaña PROGRAMADA o EN_PROCESO")
        
        elif nuevo_estado == EstadoCampania.BORRADOR:
             raise BusinessRuleError("No se puede regresar una campaña a BORRADOR manualmente")

        campania.estado = nuevo_estado
        self.db.commit()
        self.db.refresh(campania)
        
        auditoria_registro = AuditoriaModel(
            id_administrador=current_admin_id,
            accion=TipoAccion.ACTUALIZAR,
            modulo=TipoModulo.CAMPANIA,
            descripcion=f"Campaña actualizada {campania.nombre} de asunto {campania.asunto}"
        )
        self.sistema_repository.create_auditoria(auditoria_registro)
        
        return campania

    def eliminar_campania(self, id_campania: int, current_admin_id: int):
        campania = self.obtener_por_id(id_campania)
        self.repo.delete(id_campania)
        auditoria_registro = AuditoriaModel(
            id_administrador=current_admin_id,
            accion=TipoAccion.ELIMINAR,
            modulo=TipoModulo.CAMPANIA,
            descripcion=f"Campaña eliminada {campania.nombre} de asunto {campania.asunto}"
        )
        self.sistema_repository.create_auditoria(auditoria_registro)
        return campania

    def _gestionar_destinatarios(self, id_campania: int, agregar: list = None, eliminar: list = None):
        if eliminar:
            self.db.query(CampaniaDestinatario).filter(
                CampaniaDestinatario.id_campania_email == id_campania,
                CampaniaDestinatario.id_estudiante.in_(eliminar)
            ).delete(synchronize_session=False)
        
        if agregar:
            # Validar que los IDs de estudiante existan
            estudiantes_validos = self.db.query(EstudianteModel.id_estudiante).filter(
                EstudianteModel.id_estudiante.in_(agregar)
            ).all()
            ids_validos = {e.id_estudiante for e in estudiantes_validos}
            ids_invalidos = set(agregar) - ids_validos
            if ids_invalidos:
                raise BusinessRuleError(f"Los siguientes estudiantes no existen: {sorted(ids_invalidos)}")

            existentes = self.db.query(CampaniaDestinatario.id_estudiante).filter(
                CampaniaDestinatario.id_campania_email == id_campania,
                CampaniaDestinatario.id_estudiante.in_(agregar)
            ).all()
            existentes_ids = [e[0] for e in existentes]
            
            nuevos = [
                CampaniaDestinatario(id_campania_email=id_campania, id_estudiante=est_id)
                for est_id in agregar if est_id not in existentes_ids
            ]
            if nuevos:
                self.db.bulk_save_objects(nuevos)