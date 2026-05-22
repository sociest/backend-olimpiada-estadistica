from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import time
from fastapi.responses import JSONResponse

from app.core.responses import PaginatedData, PaginatedResponse, PaginationMeta, ResponseBase
from app.db.database import get_db
from app.modules.avisos.aviso_service import AvisoService
from app.modules.categorias.categoria_service import CategoriaService
from app.modules.convocatorias.convocatoria_service import ConvocatoriaService
from app.modules.fases.fase_service import FaseService
from app.modules.materiales.material_service import MaterialService
from app.modules.personas.persona_service import PersonaService
from app.modules.public_bff.public_schema import (
    ConvocatoriaDetalleDTO,
    FasePreparacionPublicaDTO,
    FasePruebaPublicaDTO,
    InicioResponseDTO,
    MaterialPublicoSimpleDTO,
    ColegioPublicoSimpleDTO,
)
from app.modules.public_bff.public_service import PublicBffService
from app.modules.colegios.colegio_service import ColegioService


router = APIRouter(prefix="/public", tags=["public"])


def _get_service(db: Session) -> PublicBffService:
    return PublicBffService(
        convocatoria_service=ConvocatoriaService(db),
        categoria_service=CategoriaService(db),
        aviso_service=AvisoService(db),
        material_service=MaterialService(db),
        fase_service=FaseService(db),
        persona_service=PersonaService(db),
        colegio_service=ColegioService(db),
    )


@router.get("/inicio", response_model=ResponseBase[InicioResponseDTO])
async def obtener_inicio(db: Session = Depends(get_db)):
    service = _get_service(db)
    data = await service.get_inicio()
    return ResponseBase(data=data, message="Operacion exitosa")


@router.get("/acerca-de/personal", response_model=ResponseBase[list])
async def obtener_personal(
    tipo: str,
    db: Session = Depends(get_db),
):
    service = _get_service(db)
    items = await service.get_personal(tipo)
    return ResponseBase(data=items, message="Lista obtenida correctamente")


@router.get("/convocatorias/{convocatoria_id}/detalle", response_model=ResponseBase[ConvocatoriaDetalleDTO])
async def obtener_convocatoria_detalle(convocatoria_id: int, db: Session = Depends(get_db)):
    service = _get_service(db)
    data = await service.get_convocatoria_detalle(convocatoria_id)
    return ResponseBase(data=data, message="Operacion exitosa")


@router.get(
    "/categorias/{categoria_id}/fases",
    response_model=ResponseBase[list[FasePreparacionPublicaDTO | FasePruebaPublicaDTO]],
)
async def obtener_fases_por_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
):
    service = _get_service(db)
    items = await service.get_fases_por_categoria(categoria_id)
    return ResponseBase(data=items, message="Lista obtenida correctamente")


@router.get("/fases/{fase_id}/materiales", response_model=ResponseBase[list[MaterialPublicoSimpleDTO]])
async def obtener_materiales_por_fase(
    fase_id: int,
    db: Session = Depends(get_db),
):
    service = _get_service(db)
    items = await service.get_materiales_por_fase(fase_id)
    return ResponseBase(data=items, message="Lista obtenida correctamente")

# @router.get("/colegios", response_model=ResponseBase[list[ColegioPublicoSimpleDTO]])
# async def obtener_colegios(db: Session = Depends(get_db)):
#     service = _get_service(db)
#     items = await service.get_colegios_minified()
#     return ResponseBase(data=items, message="Lista de colegios obtenida correctamente")

@router.get("/colegios")
async def obtener_colegios(db: Session = Depends(get_db)):
    t0 = time.time()
    
    service = _get_service(db)
    items = await service.get_colegios_minified()
    
    t1 = time.time()
    print(f"⏱️ Tiempo de Base de Datos y Servicio: {t1 - t0} segundos")
    
    # Retornamos JSON directo, saltando la validación profunda de Pydantic
    return JSONResponse(content={
        "status": "success",
        "data": items,
        "message": "Lista de colegios obtenida correctamente"
    })