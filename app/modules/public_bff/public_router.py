from typing import List
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.responses import PaginatedData, PaginatedResponse, PaginationMeta
from app.core.dependencies import limiter
from app.modules.personas.persona_model import TipoColaborador
from app.modules.personas.persona_service import PersonaService
from app.modules.public_bff.public_schema import PublicColaboradorResponseDTO
from app.modules.colegios.colegio_schema import ColegioPublicoMinifiedDTO
from app.modules.colegios.colegio_service import ColegioService
from app.core.responses import ResponseBase

router = APIRouter(prefix="/public", tags=["public"])

@router.get(
    "/colaboradores", 
    response_model=PaginatedResponse[PublicColaboradorResponseDTO]
)
@limiter.limit("10/minute")
def get_colaboradores_public(
    request: Request,
    tipo: TipoColaborador = Query(..., description="Tipo de colaborador"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1),
    db: Session = Depends(get_db)
):
    service = PersonaService(db)
    items, total = service.get_colaboradores_activos_by_tipo(tipo, page, limit)
    
    meta = PaginationMeta(
        page=page, 
        limit=limit, 
        total=total, 
        total_pages=(total + limit - 1) // limit
    )
    data = PaginatedData(items=items, meta=meta)
    
    return PaginatedResponse(
        data=data, 
        message=f"Colaboradores de tipo '{tipo.value}' obtenidos correctamente"
    )

@router.get(
    "/colegios-minified", 
    response_model=ResponseBase[List[ColegioPublicoMinifiedDTO]]
)
@limiter.limit("10/minute")
async def obtener_colegios_minified_public(
    request: Request,
    db: Session = Depends(get_db)
):
    service = ColegioService(db)
    colegios = await service.get_colegios_minified()
    
    return ResponseBase(
        data=colegios, 
        message="Lista simplificada de colegios obtenida correctamente"
    )