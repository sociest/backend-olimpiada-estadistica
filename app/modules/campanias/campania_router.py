from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.db.database import get_db
from app.modules.campanias.campania_model import EstadoCampania
from app.modules.campanias.campania_schema import CampaniaCreateDTO, CampaniaUpdateDTO, CampaniaResponseDTO, EstadoUpdateDTO
from app.modules.campanias.campania_service import CampaniaService
from app.core.responses import ResponseBase, PaginatedResponse, PaginationMeta
from app.core.dependencies import get_current_admin

router = APIRouter(prefix="/campanias", tags=["Campañas"])

@router.get("/", response_model=PaginatedResponse[CampaniaResponseDTO])
def listar_campanias(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    nombre: Optional[str] = None,
    asunto: Optional[str] = None,
    estado: Optional[EstadoCampania] = None,
    creacion_start: Optional[datetime] = None,
    creacion_end: Optional[datetime] = None,
    prog_start: Optional[datetime] = None,
    prog_end: Optional[datetime] = None,
    inicio_start: Optional[datetime] = None,
    inicio_end: Optional[datetime] = None,
    fin_start: Optional[datetime] = None,
    fin_end: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = CampaniaService(db)
    items, total = service.listar_campanias(
        page, limit, nombre=nombre, asunto=asunto, estado=estado,
        creacion_start=creacion_start, creacion_end=creacion_end,
        prog_start=prog_start, prog_end=prog_end,
        inicio_start=inicio_start, inicio_end=inicio_end,
        fin_start=fin_start, fin_end=fin_end
    )
    total_pages = (total + limit - 1) // limit
    return PaginatedResponse(
        success=True,
        message="Campañas listadas exitosamente",
        data={
            "items": items,
            "meta": PaginationMeta(page=page, limit=limit, total=total, total_pages=total_pages)
        }
    )

@router.get("/{id}", response_model=ResponseBase[CampaniaResponseDTO])
def obtener_campania(id: int, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = CampaniaService(db)
    campania = service.obtener_por_id(id)
    return ResponseBase(success=True, message="Campaña encontrada", data=campania)

@router.post("/", response_model=ResponseBase[CampaniaResponseDTO])
def crear_campania(data: CampaniaCreateDTO, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = CampaniaService(db)
    campania = service.crear_campania(data, current_admin_id)
    return ResponseBase(success=True, message="Campaña creada en borrador", data=campania)

@router.put("/{id}", response_model=ResponseBase[CampaniaResponseDTO])
def actualizar_campania(id: int, data: CampaniaUpdateDTO, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = CampaniaService(db)
    campania = service.actualizar_campania(id, data, current_admin_id)
    return ResponseBase(success=True, message="Campaña actualizada", data=campania)

@router.patch("/{id}/estado", response_model=ResponseBase[CampaniaResponseDTO])
def cambiar_estado(id: int, data: EstadoUpdateDTO, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = CampaniaService(db)
    campania = service.cambiar_estado(id, data.estado, current_admin_id)
    return ResponseBase(success=True, message=f"Estado cambiado a {data.estado}", data=campania)

@router.delete("/{id}")
def eliminar_campania(id: int, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = CampaniaService(db)
    service.eliminar_campania(id, current_admin_id)
    return ResponseBase(success=True, message="Campaña eliminada permanentemente", data=None)
