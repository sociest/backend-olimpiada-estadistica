from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.dependencies import get_current_admin
from app.core.responses import PaginatedData, PaginatedResponse, ResponseBase, PaginationMeta
from app.modules.sistema.sistema_model import TipoAccion, TipoModulo
from app.modules.sistema.sistema_schema import (
    AuditoriaResponseDTO,
    ActividadSistemaResponseDTO,
    AdminDashboardResponseDTO
)
from app.modules.sistema.sistema_service import SistemaService


router = APIRouter(prefix="/sistema", tags=["sistema"])


@router.get("/auditoria", response_model=PaginatedResponse[AuditoriaResponseDTO])
def listar_auditoria(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1),
    fecha_start: Optional[datetime] = None,
    fecha_end: Optional[datetime] = None,
    modulo: Optional[TipoModulo] = None,
    accion: Optional[TipoAccion] = None,
    busqueda: Optional[str] = None,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    service = SistemaService(db)
    skip = (page - 1) * limit
    items, total = service.get_auditorias(skip, limit, fecha_start, fecha_end, modulo, accion, busqueda)
    
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    data = PaginatedData(items=items, meta=meta)
    
    return PaginatedResponse(data=data, message="Registros de auditoría obtenidos correctamente")


@router.get("/auditoria/exportar/csv", response_class=Response)
def exportar_auditoria_csv(
    fecha_start: datetime = Query(...),
    fecha_end: datetime = Query(...),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    service = SistemaService(db)
    csv_content = service.exportar_csv(fecha_start, fecha_end)
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=auditoria_{fecha_start.date()}_a_{fecha_end.date()}.csv"}
    )


@router.get("/actividades", response_model=PaginatedResponse[ActividadSistemaResponseDTO])
def listar_actividades(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    service = SistemaService(db)
    skip = (page - 1) * limit
    items, total = service.get_actividades(skip, limit)
    
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    data = PaginatedData(items=items, meta=meta)
    
    return PaginatedResponse(data=data, message="Actividades del sistema obtenidas correctamente")


@router.get("/admin-dashboard", response_model=ResponseBase[AdminDashboardResponseDTO])
def obtener_dashboard_admin(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    service = SistemaService(db)
    dashboard_data = service.get_admin_dashboard()
    
    return ResponseBase(data=dashboard_data, message="Información del dashboard cargada correctamente")