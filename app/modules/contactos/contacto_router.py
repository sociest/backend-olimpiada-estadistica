from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.dependencies import get_current_admin, limiter, verify_bot_protection
from app.core.responses import PaginatedData, PaginatedResponse, PaginationMeta, ResponseBase
from app.db.database import get_db
from app.modules.contactos.contacto_schema import (
    ContactoCreateDTO, ContactoRequestDTO, ContactoResponseDTO, 
    ContactoCompletoResponseDTO, ContactoRespuestaCreateDTO
)
from app.modules.contactos.contacto_model import EstadoContacto
from app.modules.contactos.contacto_service import ContactoService
from app.modules.email_logs.email_log_model import EstadoEmail

router = APIRouter(prefix="/contactos", tags=["contactos"])

@router.post("", response_model=ResponseBase[ContactoResponseDTO])
@limiter.limit("3/minute")
async def crear_contacto(request: Request, data: ContactoRequestDTO, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else None
    await verify_bot_protection(data.cf_turnstile_response, data.username_hp, client_ip)
    
    clean_data = ContactoCreateDTO(**data.model_dump(exclude={"username_hp", "cf_turnstile_response"}))
    service = ContactoService(db)
    contacto = service.create(clean_data)
    return ResponseBase(data=contacto, message="Mensaje enviado correctamente")

@router.get("", response_model=PaginatedResponse[ContactoResponseDTO])
def listar_contactos(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    correo_electronico: Optional[str] = None,
    estado: Optional[EstadoContacto] = None,
    creacion_start: Optional[datetime] = None,
    creacion_end: Optional[datetime] = None,
    cambio_start: Optional[datetime] = None,
    cambio_end: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = ContactoService(db)
    items, total = service.get_all(
        page, limit, correo_electronico=correo_electronico, estado=estado,
        creacion_start=creacion_start, creacion_end=creacion_end,
        cambio_start=cambio_start, cambio_end=cambio_end
    )
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    return PaginatedResponse(data=PaginatedData(items=items, meta=meta), message="Lista obtenida")

@router.get("/respondidos", response_model=PaginatedResponse[ContactoCompletoResponseDTO])
def listar_contactos_respondidos(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    cambio_start: Optional[datetime] = None,
    cambio_end: Optional[datetime] = None,
    estado_email: Optional[EstadoEmail] = None,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = ContactoService(db)
    items, total = service.get_all_respondidos(
        page, limit, cambio_start=cambio_start, cambio_end=cambio_end, estado_email=estado_email
    )
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    return PaginatedResponse(data=PaginatedData(items=items, meta=meta), message="Respondidos obtenidos")

@router.get("/{contacto_id}", response_model=ResponseBase[ContactoCompletoResponseDTO])
def obtener_contacto(
    contacto_id: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = ContactoService(db)
    contacto = service.get_by_id(contacto_id)
    return ResponseBase(data=contacto, message="Operacion exitosa")

@router.patch("/{contacto_id}/marcar-leido", response_model=ResponseBase[ContactoResponseDTO])
def marcar_contacto_leido(
    contacto_id: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = ContactoService(db)
    contacto = service.marcar_leido(contacto_id, current_admin_id)
    return ResponseBase(data=contacto, message="Contacto marcado como leído")

@router.post("/{contacto_id}/responder", response_model=ResponseBase[ContactoCompletoResponseDTO])
def responder_contacto(
    contacto_id: int,
    data: ContactoRespuestaCreateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = ContactoService(db)
    contacto = service.responder(contacto_id, data, current_admin_id)
    return ResponseBase(data=contacto, message="Respuesta encolada para envío")

@router.delete("/{contacto_id}", response_model=ResponseBase[None])
def eliminar_contacto(
    contacto_id: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = ContactoService(db)
    service.delete(contacto_id, current_admin_id)
    return ResponseBase(data=None, message="Contacto eliminado exitosamente")
