from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin
from app.core.responses import PaginatedData, PaginatedResponse, PaginationMeta, ResponseBase
from app.db.database import get_db
from app.modules.avisos.aviso_model import AvisoPrioridad, EstadoAviso, TipoAviso
from app.modules.avisos.aviso_schema import AvisoCreateDTO, AvisoResponseDTO, AvisoUpdateDTO, AvisoEstadoUpdateDTO
from app.modules.avisos.aviso_service import AvisoService

router = APIRouter(prefix="/avisos", tags=["avisos"])

@router.get("", response_model=PaginatedResponse[AvisoResponseDTO])
def listar_avisos_publicos(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    titulo: Optional[str] = None,
    descripcion: Optional[str] = None,
    tipo: Optional[TipoAviso] = None,
    prioridad: Optional[AvisoPrioridad] = None,
    fecha_creacion: Optional[date] = None,
    fecha_publicacion: Optional[date] = None,
    db: Session = Depends(get_db)
):
    filters = {
        "titulo": titulo,
        "descripcion": descripcion,
        "tipo": tipo,
        "prioridad": prioridad,
        "fecha_creacion": fecha_creacion,
        "fecha_publicacion": fecha_publicacion
    }
    service = AvisoService(db)
    items, total = service.get_public(page=page, limit=limit, filters=filters)
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    data = PaginatedData(items=items, meta=meta)
    return PaginatedResponse(data=data, message="Avisos públicos obtenidos correctamente")

@router.get("/admin", response_model=PaginatedResponse[AvisoResponseDTO])
def listar_avisos_admin(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    titulo: Optional[str] = None,
    descripcion: Optional[str] = None,
    tipo: Optional[TipoAviso] = None,
    prioridad: Optional[AvisoPrioridad] = None,
    estado: Optional[EstadoAviso] = None,
    fecha_creacion: Optional[date] = None,
    fecha_publicacion: Optional[date] = None,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    filters = {
        "titulo": titulo,
        "descripcion": descripcion,
        "tipo": tipo,
        "prioridad": prioridad,
        "estado": estado,
        "fecha_creacion": fecha_creacion,
        "fecha_publicacion": fecha_publicacion
    }
    service = AvisoService(db)
    items, total = service.get_all(page=page, limit=limit, filters=filters)
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    data = PaginatedData(items=items, meta=meta)
    return PaginatedResponse(data=data, message="Lista obtenida correctamente")

@router.get("/{aviso_id}", response_model=ResponseBase[AvisoResponseDTO])
def obtener_aviso(aviso_id: int, db: Session = Depends(get_db)):
    service = AvisoService(db)
    aviso = service.get_public_by_id(aviso_id)
    return ResponseBase(data=aviso, message="Operacion exitosa")

@router.get("/admin/{aviso_id}", response_model=ResponseBase[AvisoResponseDTO])
def obtener_aviso_admin(
    aviso_id: int, 
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = AvisoService(db)
    aviso = service.get_by_id(aviso_id)
    return ResponseBase(data=aviso, message="Operacion exitosa")

@router.post("", response_model=ResponseBase[AvisoResponseDTO])
def crear_aviso(
    data: AvisoCreateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = AvisoService(db)
    aviso = service.create(data, current_admin_id)
    return ResponseBase(data=aviso, message="Aviso creado exitosamente")

@router.put("/{aviso_id}", response_model=ResponseBase[AvisoResponseDTO])
def actualizar_aviso(
    aviso_id: int,
    data: AvisoUpdateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = AvisoService(db)
    aviso = service.update(aviso_id, data, current_admin_id)
    return ResponseBase(data=aviso, message="Aviso actualizado exitosamente")

@router.patch("/{aviso_id}/estado", response_model=ResponseBase[AvisoResponseDTO])
def cambiar_estado_aviso(
    aviso_id: int,
    data: AvisoEstadoUpdateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = AvisoService(db)
    aviso = service.cambiar_estado(aviso_id, data, current_admin_id)
    return ResponseBase(data=aviso, message="Estado actualizado exitosamente")

@router.delete("/{aviso_id}", response_model=ResponseBase[AvisoResponseDTO])
def eliminar_aviso(
    aviso_id: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = AvisoService(db)
    aviso = service.delete(aviso_id, current_admin_id)
    return ResponseBase(data=aviso, message="Aviso eliminado exitosamente")
