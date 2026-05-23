from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin, limiter, verify_bot_protection
from app.core.responses import PaginatedData, PaginatedResponse, PaginationMeta, ResponseBase
from app.db.database import get_db
from app.modules.contactos.contacto_schema import ContactoCreateDTO, ContactoRequestDTO, ContactoResponseDTO, ContactoUpdateDTO
from app.modules.contactos.contacto_service import ContactoService

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
    page: int = 1,
    limit: int = 10,
    correo_electronico: str | None = None,
    estado: str | None = None,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = ContactoService(db)
    items, total = service.get_all(page=page, limit=limit, correo_electronico=correo_electronico, estado=estado)
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    data = PaginatedData(items=items, meta=meta)
    return PaginatedResponse(data=data, message="Lista obtenida correctamente")

@router.get("/{contacto_id}", response_model=ResponseBase[ContactoResponseDTO])
def obtener_contacto(
    contacto_id: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = ContactoService(db)
    contacto = service.get_by_id(contacto_id)
    return ResponseBase(data=contacto, message="Operacion exitosa")

@router.patch("/{contacto_id}", response_model=ResponseBase[ContactoResponseDTO])
def actualizar_contacto(
    contacto_id: int,
    data: ContactoUpdateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = ContactoService(db)
    contacto = service.update(contacto_id, data, current_admin_id)
    return ResponseBase(data=contacto, message="Operacion exitosa")

@router.delete("/{contacto_id}", response_model=ResponseBase[ContactoResponseDTO])
def eliminar_contacto(
    contacto_id: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = ContactoService(db)
    contacto = service.delete(contacto_id, current_admin_id)
    return ResponseBase(data=contacto, message="Operacion exitosa")