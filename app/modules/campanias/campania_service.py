from sqlalchemy.orm import Session
from datetime import datetime
from app.core.exceptions import BusinessRuleError, NotFoundError
from app.modules.campanias.campania_model import CampaniaEmail, CampaniaDestinatario, EstadoCampania
from app.modules.campanias.campania_schema import CampaniaCreateDTO, CampaniaUpdateDTO
from app.modules.estudiantes.estudiante_model import EstudianteModel

class CampaniaService:
    def __init__(self, db: Session):
        self.db = db

    def crear_campania(self, data: CampaniaCreateDTO) -> CampaniaEmail:
        nueva = CampaniaEmail(
            nombre=data.nombre,
            asunto=data.asunto,
            fecha_programada=data.fecha_programada,
            estado=EstadoCampania.BORRADOR
        )
        self.db.add(nueva)
        self.db.commit()
        self.db.refresh(nueva)

        if data.destinatarios_ids:
            self._gestionar_destinatarios(nueva.id, agregar=data.destinatarios_ids)
            
        return nueva

    def actualizar_campania(self, id_campania: int, data: CampaniaUpdateDTO) -> CampaniaEmail:
        campania = self.db.query(CampaniaEmail).filter(CampaniaEmail.id == id_campania).first()
        if not campania:
            raise NotFoundError("Campaña no encontrada")
        
        if campania.estado != EstadoCampania.BORRADOR:
            raise BusinessRuleError("Solo se pueden editar campañas en estado BORRADOR")

        if data.nombre: campania.nombre = data.nombre
        if data.asunto: campania.asunto = data.asunto
        if data.fecha_programada: campania.fecha_programada = data.fecha_programada

        self.db.commit()
        
        if data.agregar_destinatarios or data.eliminar_destinatarios:
            self._gestionar_destinatarios(campania.id, data.agregar_destinatarios, data.eliminar_destinatarios)

        self.db.refresh(campania)
        return campania

    def _gestionar_destinatarios(self, id_campania: int, agregar: list = None, eliminar: list = None):
        if eliminar:
            self.db.query(CampaniaDestinatario).filter(
                CampaniaDestinatario.id_campania == id_campania,
                CampaniaDestinatario.id_estudiante.in_(eliminar)
            ).delete(synchronize_session=False)
        
        if agregar:
            existentes = self.db.query(CampaniaDestinatario.id_estudiante).filter(
                CampaniaDestinatario.id_campania == id_campania,
                CampaniaDestinatario.id_estudiante.in_(agregar)
            ).all()
            existentes_ids = [e[0] for e in existentes]
            
            nuevos = [
                CampaniaDestinatario(id_campania=id_campania, id_estudiante=est_id) 
                for est_id in agregar if est_id not in existentes_ids
            ]
            if nuevos:
                self.db.bulk_save_objects(nuevos)
        
        self.db.commit()

    def cambiar_estado(self, id_campania: int, nuevo_estado: EstadoCampania):
        campania = self.db.query(CampaniaEmail).filter(CampaniaEmail.id == id_campania).first()
        if not campania:
            raise NotFoundError("Campaña no encontrada")

        if nuevo_estado == EstadoCampania.PROGRAMADA:
            if campania.estado not in (EstadoCampania.BORRADOR, EstadoCampania.CANCELADA):
                raise BusinessRuleError("Solo se puede programar desde BORRADOR o CANCELADA")
            total_dest = self.db.query(CampaniaDestinatario).filter_by(id_campania=id_campania).count()
            if total_dest == 0:
                raise BusinessRuleError("No se puede programar una campaña sin destinatarios")
                
        elif nuevo_estado == EstadoCampania.CANCELADA:
            if campania.estado not in (EstadoCampania.PROGRAMADA, EstadoCampania.EN_PROCESO):
                raise BusinessRuleError("Solo se puede cancelar una campaña PROGRAMADA o EN_PROCESO")

        campania.estado = nuevo_estado
        self.db.commit()
        self.db.refresh(campania)
        return campania