from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin, limiter, verify_bot_protection
from app.core.responses import PaginatedData, PaginatedResponse, PaginationMeta, ResponseBase
from app.db.database import get_db
from app.modules.inscripciones.inscripcion_schema import (
    InscripcionFormularioDTO,
    InscripcionFormularioRequestDTO,
    InscripcionFormularioResponseDTO,
    InscripcionResponseDTO,
    EstudianteBuscarDTO,
    EstudianteBuscarRequestDTO,
    EstudianteBusquedaResponseDTO,
)
from app.modules.inscripciones.inscripcion_service import InscripcionService

router = APIRouter(prefix="/inscripciones", tags=["inscripciones"])

@router.post("/formulario", response_model=ResponseBase[InscripcionFormularioResponseDTO])
@limiter.limit("5/minute")
async def registrar_inscripcion_formulario(
    request: Request, 
    data: InscripcionFormularioRequestDTO, 
    db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else None
    await verify_bot_protection(data.cf_turnstile_response, data.username_hp, client_ip)

    clean_data = InscripcionFormularioDTO(**data.model_dump(exclude={"username_hp", "cf_turnstile_response"}))

    service = InscripcionService(db)
    resultado = service.registrar_formulario(clean_data)
    
    return ResponseBase(data=resultado, message="Inscripcion registrada correctamente")

@router.get("", response_model=PaginatedResponse[InscripcionResponseDTO])
def listar_inscripciones(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = InscripcionService(db)
    items, total = service.list_all(page=page, limit=limit)
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    data = PaginatedData(items=items, meta=meta)
    return PaginatedResponse(data=data, message="Lista obtenida correctamente")

@router.post("/verificar-estudiante", response_model=ResponseBase[EstudianteBusquedaResponseDTO])
@limiter.limit("5/minute")
async def verificar_estudiante_existente(
    request: Request, 
    data: EstudianteBuscarRequestDTO, 
    db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else None
    await verify_bot_protection(data.cf_turnstile_response, data.username_hp, client_ip)

    service = InscripcionService(db)
    resultado = service.buscar_estudiante_registro(data.carnet_identidad, data.fecha_nacimiento)
    
    return ResponseBase(data=resultado, message="Estudiante localizado con éxito")