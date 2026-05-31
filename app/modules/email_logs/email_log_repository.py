from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_
from typing import Optional
from datetime import datetime
from app.modules.email_logs.email_log_model import EmailLog, EstadoEmail, TipoEmail

class EmailLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def _apply_eager_loading(self, query):
        return query.options(
            selectinload(EmailLog.estudiante),
            selectinload(EmailLog.contacto),
            selectinload(EmailLog.campania)
        )

    def get_all(self, skip: int, limit: int, tipo: Optional[TipoEmail], estado: Optional[EstadoEmail], 
                id_campania: Optional[int], es_estudiante: Optional[bool], es_contacto: Optional[bool], es_campania: Optional[bool],
                busqueda: Optional[str], creacion_start: Optional[datetime], creacion_end: Optional[datetime],
                envio_start: Optional[datetime], envio_end: Optional[datetime],
                intento_start: Optional[datetime], intento_end: Optional[datetime]):
        
        query = self.db.query(EmailLog)
        
        if tipo: query = query.filter(EmailLog.tipo == tipo)
        if estado: query = query.filter(EmailLog.estado == estado)
        if id_campania: query = query.filter(EmailLog.id_campania == id_campania)
        
        if es_estudiante: query = query.filter(EmailLog.id_estudiante.isnot(None))
        if es_contacto: query = query.filter(EmailLog.id_contacto.isnot(None))
        if es_campania: query = query.filter(EmailLog.id_campania.isnot(None))
            
        if busqueda:
            query = query.filter(or_(EmailLog.asunto.ilike(f"%{busqueda}%"), EmailLog.destinatario.ilike(f"%{busqueda}%")))

        if creacion_start and creacion_end: query = query.filter(EmailLog.fecha_creacion.between(creacion_start, creacion_end))
        if envio_start and envio_end: query = query.filter(EmailLog.fecha_envio.between(envio_start, envio_end))
        if intento_start and intento_end: query = query.filter(EmailLog.ultimo_intento.between(intento_start, intento_end))
        
        total = query.count()
        query = self._apply_eager_loading(query)
        items = query.order_by(EmailLog.fecha_creacion.desc()).offset(skip).limit(limit).all()
        return items, total

    def get_by_id(self, id_log: int) -> EmailLog:
        query = self.db.query(EmailLog).filter(EmailLog.id_email_log == id_log)
        query = self._apply_eager_loading(query)
        return query.first()
