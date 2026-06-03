from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin
from app.core.responses import PaginatedData, PaginatedResponse, ResponseBase, PaginationMeta
from app.db.database import get_db
from app.modules.convocatorias.convocatoria_model import EstadoConvocatoria, EstadoTemporal
from app.modules.convocatorias.convocatoria_schema import (
    ConvocatoriaCreateDTO,
    ConvocatoriaResponseDTO,
    ConvocatoriaUpdateDTO,
    ConvocatoriaEstadisticasCTO
)
from app.modules.convocatorias.convocatoria_service import ConvocatoriaService


router = APIRouter(prefix="/convocatorias", tags=["convocatorias"])


@router.get("", response_model=PaginatedResponse[ConvocatoriaResponseDTO])
def listar_convocatorias(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    estado: Optional[EstadoConvocatoria] = None,
    estado_temporal: Optional[EstadoTemporal] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = ConvocatoriaService(db)
    items, total = service.get_all(page, limit, estado, estado_temporal, start_date, end_date)
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    data = PaginatedData(items=items, meta=meta)
    return PaginatedResponse(data=data, message="Lista de convocatorias obtenida correctamente")


@router.get("/{convocatoria_id}", response_model=ResponseBase[ConvocatoriaResponseDTO])
def obtener_convocatoria(convocatoria_id: int, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = ConvocatoriaService(db)
    convocatoria_dict = service.get_by_id(convocatoria_id)
    return ResponseBase(data=convocatoria_dict, message="Operación exitosa")


@router.post("", response_model=ResponseBase[ConvocatoriaResponseDTO])
def crear_convocatoria(
    data: ConvocatoriaCreateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = ConvocatoriaService(db)
    convocatoria_dict = service.create(data, current_admin_id)
    return ResponseBase(data=convocatoria_dict, message="Convocatoria creada exitosamente en borrador")


@router.put("/{convocatoria_id}", response_model=ResponseBase[ConvocatoriaResponseDTO])
def actualizar_convocatoria(
    convocatoria_id: int,
    data: ConvocatoriaUpdateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = ConvocatoriaService(db)
    convocatoria_dict = service.update(convocatoria_id, data, current_admin_id)
    return ResponseBase(data=convocatoria_dict, message="Convocatoria actualizada exitosamente")


@router.put("/{convocatoria_id}/publicar", response_model=ResponseBase[ConvocatoriaResponseDTO])
def publicar_convocatoria(
    convocatoria_id: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = ConvocatoriaService(db)
    convocatoria_dict = service.cambiar_estado(convocatoria_id, EstadoConvocatoria.PUBLICADA, current_admin_id)
    return ResponseBase(data=convocatoria_dict, message="Convocatoria publicada exitosamente")


@router.put("/{convocatoria_id}/ocultar", response_model=ResponseBase[ConvocatoriaResponseDTO])
def ocultar_convocatoria(
    convocatoria_id: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = ConvocatoriaService(db)
    convocatoria_dict = service.cambiar_estado(convocatoria_id, EstadoConvocatoria.OCULTA, current_admin_id)
    return ResponseBase(data=convocatoria_dict, message="Convocatoria ocultada exitosamente")


@router.put("/{convocatoria_id}/cancelar", response_model=ResponseBase[ConvocatoriaResponseDTO])
def cancelar_convocatoria(
    convocatoria_id: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = ConvocatoriaService(db)
    convocatoria_dict = service.cambiar_estado(convocatoria_id, EstadoConvocatoria.CANCELADA, current_admin_id)
    return ResponseBase(data=convocatoria_dict, message="Convocatoria cancelada exitosamente")

@router.delete("/{convocatoria_id}", response_model=ResponseBase[dict])
def eliminar_convocatoria_fisica(
    convocatoria_id: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = ConvocatoriaService(db)
    resultado = service.delete(convocatoria_id, current_admin_id)
    return ResponseBase(data=resultado, message="Convocatoria eliminada físicamente del sistema")


@router.get("/{convocatoria_id}/estadisticas", response_model=ResponseBase[ConvocatoriaEstadisticasCTO])
async def obtener_estadisticas(
    convocatoria_id:int,
    db: Session = Depends(get_db)
):
    service = ConvocatoriaService(db)
    resultado = service.get_conv_dashboard(convocatoria_id)
    return ResponseBase(data = resultado, message="Estadisticas conseguidas correctamente")