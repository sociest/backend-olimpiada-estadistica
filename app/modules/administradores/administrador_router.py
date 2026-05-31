from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin
from app.core.responses import PaginatedData, PaginatedResponse, PaginationMeta, ResponseBase
from app.db.database import get_db
from app.modules.administradores.administrador_schema import (
    AdministradorCreateDTO,
    AdministradorResponseDTO,
    AdministradorUpdateDTO,
)
from app.modules.administradores.administrador_service import AdministradorService


router = APIRouter(prefix="/administradores", tags=["administradores"])


@router.get("", response_model=PaginatedResponse[AdministradorResponseDTO])
def listar_administradores(
    page: int = 1,
    limit: int = 10,
    nombre: str | None = None,
    correo: str | None = None,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = AdministradorService(db)
    items, total = service.get_all(page=page, limit=limit, nombre=nombre, correo=correo)
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    data = PaginatedData(items=items, meta=meta)
    return PaginatedResponse(data=data, message="Lista obtenida correctamente")


@router.get("/{administrador_id}", response_model=ResponseBase[AdministradorResponseDTO])
def obtener_administrador(
    administrador_id: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = AdministradorService(db)
    administrador = service.get_by_id(administrador_id)
    return ResponseBase(data=administrador, message="Operacion exitosa")


@router.post("", response_model=ResponseBase[AdministradorResponseDTO])
def crear_administrador(
    data: AdministradorCreateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = AdministradorService(db)
    administrador = service.create(data, current_admin_id)
    return ResponseBase(data=administrador, message="Administrador creado correctamente")


@router.put("/{administrador_id}", response_model=ResponseBase[AdministradorResponseDTO])
def actualizar_administrador(
    administrador_id: int,
    data: AdministradorUpdateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = AdministradorService(db)
    administrador = service.update(administrador_id, data, current_admin_id)
    return ResponseBase(data=administrador, message="Administrador actualizado correctamente")


@router.patch("/{administrador_id}/baja", response_model=ResponseBase[AdministradorResponseDTO])
def baja_logica_administrador(
    administrador_id: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = AdministradorService(db)
    administrador = service.baja_logic(administrador_id, current_admin_id)
    return ResponseBase(data=administrador, message="Administrador dado de baja logicamente")


@router.patch("/{administrador_id}/alta", response_model=ResponseBase[AdministradorResponseDTO])
def alta_logica_administrador(
    administrador_id: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = AdministradorService(db)
    administrador = service.alta_logic(administrador_id, current_admin_id)
    return ResponseBase(data=administrador, message="Administrador dado de alta logicamente")


@router.delete("/{administrador_id}", response_model=ResponseBase[AdministradorResponseDTO])
def eliminar_administrador(
    administrador_id: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = AdministradorService(db)
    administrador = service.delete_total(administrador_id, current_admin_id)
    return ResponseBase(data=administrador, message="Administrador eliminado permanentemente")
