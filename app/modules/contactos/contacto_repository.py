from sqlalchemy.orm import Session, selectinload
from sqlalchemy import case
from typing import Optional
from datetime import datetime

from app.modules.contactos.contacto_model import ContactoModel, EstadoContacto
from app.modules.email_logs.email_log_model import EmailLog, EstadoEmail

class ContactoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, contacto_id: int):
        return self.db.query(ContactoModel)\
            .options(selectinload(ContactoModel.email_logs))\
            .filter(ContactoModel.id_contacto == contacto_id).first()

    def get_all(self, skip: int, limit: int, correo_electronico: Optional[str] = None, estado: Optional[EstadoContacto] = None,
                creacion_start: Optional[datetime] = None, creacion_end: Optional[datetime] = None,
                cambio_start: Optional[datetime] = None, cambio_end: Optional[datetime] = None):
        
        query = self.db.query(ContactoModel)
        
        if correo_electronico:
            query = query.filter(ContactoModel.correo_electronico.ilike(f"%{correo_electronico}%"))
        if estado:
            query = query.filter(ContactoModel.estado == estado)
            
        if creacion_start and creacion_end: query = query.filter(ContactoModel.fecha_creacion.between(creacion_start, creacion_end))
        if cambio_start and cambio_end: query = query.filter(ContactoModel.fecha_actualizacion.between(cambio_start, cambio_end))

        order_rule = case(
            (ContactoModel.estado == EstadoContacto.PENDIENTE, ContactoModel.fecha_creacion),
            (ContactoModel.estado == EstadoContacto.LEIDO, ContactoModel.fecha_actualizacion),
            (ContactoModel.estado == EstadoContacto.RESPONDIDO, ContactoModel.fecha_actualizacion)
        ).desc()

        total = query.count()
        items = query.order_by(order_rule).offset(skip).limit(limit).all()
        return items, total

    def get_all_respondidos(self, skip: int, limit: int, 
                            cambio_start: Optional[datetime] = None, cambio_end: Optional[datetime] = None,
                            estado_email: Optional[EstadoEmail] = None):
        
        query = self.db.query(ContactoModel).join(EmailLog, ContactoModel.id_contacto == EmailLog.id_contacto)\
            .filter(ContactoModel.estado == EstadoContacto.RESPONDIDO)

        if cambio_start and cambio_end: query = query.filter(ContactoModel.fecha_actualizacion.between(cambio_start, cambio_end))
        if estado_email: query = query.filter(EmailLog.estado == estado_email)

        query = query.options(selectinload(ContactoModel.email_logs))

        total = query.count()
        items = query.order_by(ContactoModel.fecha_actualizacion.desc()).offset(skip).limit(limit).all()
        return items, total

    def create(self, contacto: ContactoModel):
        self.db.add(contacto)
        self.db.commit()
        self.db.refresh(contacto)
        return contacto

    def update(self):
        self.db.commit()

    def delete(self, contacto: ContactoModel):
        self.db.delete(contacto)
        self.db.commit()
