from datetime import date, datetime
from typing import Optional
from sqlalchemy import case
from sqlalchemy.orm import Session
from app.modules.convocatorias.convocatoria_model import ConvocatoriaModel, EstadoConvocatoria

class ConvocatoriaRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, convocatoria_id: int):
        return (
            self.db.query(ConvocatoriaModel)
            .filter(ConvocatoriaModel.id_convocatoria == convocatoria_id)
            .first()
        )

    def get_all(self, skip: int, limit: int, estado: Optional[EstadoConvocatoria], start_date: Optional[datetime], end_date: Optional[datetime]):
        query = self.db.query(ConvocatoriaModel)

        if estado:
            query = query.filter(ConvocatoriaModel.estado == estado)
        if start_date:
            query = query.filter(ConvocatoriaModel.fecha_creacion >= start_date)
        if end_date:
            query = query.filter(ConvocatoriaModel.fecha_creacion <= end_date)

        state_order = case(
            (ConvocatoriaModel.estado == EstadoConvocatoria.PUBLICADA, 1),
            (ConvocatoriaModel.estado == EstadoConvocatoria.BORRADOR, 2),
            (ConvocatoriaModel.estado == EstadoConvocatoria.CANCELADA, 3),
            (ConvocatoriaModel.estado == EstadoConvocatoria.OCULTA, 4),
            else_=5
        )

        query = query.order_by(state_order, ConvocatoriaModel.fecha_creacion.desc())
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def get_convocatoria_activa(self) -> Optional[ConvocatoriaModel]:
        hoy = date.today()
        return (
            self.db.query(ConvocatoriaModel)
            .filter(
                ConvocatoriaModel.estado == EstadoConvocatoria.PUBLICADA,
                ConvocatoriaModel.inicio_olimpiadas <= hoy,
                ConvocatoriaModel.fin_olimpiadas >= hoy
            )
            .first()
        )
        
    def create(self, convocatoria: ConvocatoriaModel):
        self.db.add(convocatoria)
        self.db.commit()
        self.db.refresh(convocatoria)
        return convocatoria

    def update(self, convocatoria: ConvocatoriaModel):
        self.db.commit()
        self.db.refresh(convocatoria)
        return convocatoria

    def delete(self, convocatoria: ConvocatoriaModel):
        self.db.delete(convocatoria)
        self.db.commit()

    def check_overlap_fechas_global(
        self, inicio: date, fin: date, exclude_id: Optional[int] = None
    ) -> bool:
        query = self.db.query(ConvocatoriaModel).filter(
            ConvocatoriaModel.estado == EstadoConvocatoria.PUBLICADA,
            ConvocatoriaModel.inicio_olimpiadas <= fin,
            ConvocatoriaModel.fin_olimpiadas >= inicio
        )
        if exclude_id is not None:
            query = query.filter(ConvocatoriaModel.id_convocatoria != exclude_id)
        return query.first() is not None

    def get_convocatoria_principal(self) -> Optional[ConvocatoriaModel]:
        hoy = date.today()
        activa = (
            self.db.query(ConvocatoriaModel)
            .filter(
                ConvocatoriaModel.estado == EstadoConvocatoria.PUBLICADA,
                ConvocatoriaModel.inicio_olimpiadas <= hoy,
                ConvocatoriaModel.fin_olimpiadas >= hoy,
            )
            .first()
        )
        if activa:
            return activa
        proxima = (
            self.db.query(ConvocatoriaModel)
            .filter(
                ConvocatoriaModel.estado == EstadoConvocatoria.PUBLICADA,
                ConvocatoriaModel.inicio_olimpiadas > hoy,
            )
            .order_by(ConvocatoriaModel.inicio_olimpiadas.asc())
            .first()
        )
        if proxima:
            return proxima

        ultima = (
            self.db.query(ConvocatoriaModel)
            .filter(
                ConvocatoriaModel.estado == EstadoConvocatoria.PUBLICADA,
                ConvocatoriaModel.fin_olimpiadas < hoy,
            )
            .order_by(ConvocatoriaModel.fin_olimpiadas.desc())
            .first()
        )
        return ultima
    
    def get_public_by_id(self, convocatoria_id: int) -> Optional[ConvocatoriaModel]:
        return (
            self.db.query(ConvocatoriaModel)
            .filter(
                ConvocatoriaModel.id_convocatoria == convocatoria_id,
                ConvocatoriaModel.estado == EstadoConvocatoria.PUBLICADA
            )
            .first()
        )

    def get_public_convocatorias_list(self):
        return (
            self.db.query(ConvocatoriaModel)
            .filter(ConvocatoriaModel.estado == EstadoConvocatoria.PUBLICADA)
            .order_by(ConvocatoriaModel.inicio_olimpiadas.desc())
            .all()
        )