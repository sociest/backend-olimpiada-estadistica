from datetime import datetime
from typing import Optional, Tuple, List
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.modules.sistema.sistema_model import AuditoriaModel, ActividadSistemaModel, TipoAccion, TipoModulo
from app.modules.auth.auth_model import AdministradorModel  # O la ruta exacta donde lo tengas


class SistemaRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_auditorias(
        self,
        skip: int,
        limit: int,
        fecha_start: Optional[datetime],
        fecha_end: Optional[datetime],
        modulo: Optional[TipoModulo],
        accion: Optional[TipoAccion],
        busqueda: Optional[str]
    ):
        query = self.db.query(AuditoriaModel, AdministradorModel).join(
            AdministradorModel, AuditoriaModel.id_administrador == AdministradorModel.id_administrador
        )

        if fecha_start: query = query.filter(AuditoriaModel.fecha >= fecha_start)
        if fecha_end: query = query.filter(AuditoriaModel.fecha <= fecha_end)
        if modulo: query = query.filter(AuditoriaModel.modulo == modulo)
        if accion: query = query.filter(AuditoriaModel.accion == accion)
        
        if busqueda:
            query = query.filter(or_(
                AdministradorModel.nombre.ilike(f"%{busqueda}%"),
                AdministradorModel.correo.ilike(f"%{busqueda}%"),
                AuditoriaModel.descripcion.ilike(f"%{busqueda}%")
            ))

        total = query.count()
        items = query.order_by(AuditoriaModel.fecha.desc()).offset(skip).limit(limit).all()
        return items, total

    def get_auditorias_by_rango(self, fecha_start: datetime, fecha_end: datetime):
        query = self.db.query(AuditoriaModel, AdministradorModel).join(
            AdministradorModel, AuditoriaModel.id_administrador == AdministradorModel.id_administrador
        ).filter(
            AuditoriaModel.fecha >= fecha_start,
            AuditoriaModel.fecha <= fecha_end
        ).order_by(AuditoriaModel.fecha.desc())
        
        return query.all()

    def create_auditoria(self, auditoria: AuditoriaModel) -> AuditoriaModel:
        self.db.add(auditoria)
        self.db.commit()
        self.db.refresh(auditoria)
        return auditoria

    def get_actividades(self, skip: int, limit: int):
        query = self.db.query(ActividadSistemaModel)
        total = query.count()
        items = query.order_by(ActividadSistemaModel.fecha.asc()).offset(skip).limit(limit).all()
        return items, total

    def create_actividad(self, actividad: ActividadSistemaModel) -> ActividadSistemaModel:
        self.db.add(actividad)
        self.db.commit()
        self.db.refresh(actividad)
        return actividad