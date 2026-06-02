from typing import List
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.db.database import get_db
from app.core.responses import PaginatedData, PaginatedResponse, PaginationMeta
from app.core.dependencies import limiter
from app.modules.personas.persona_model import TipoColaborador
from app.modules.personas.persona_schema import PublicColaboradorResponseDTO
from app.modules.personas.persona_service import PersonaService
from app.modules.colegios.colegio_schema import ColegioPublicoMinifiedDTO
from app.modules.colegios.colegio_service import ColegioService
from app.core.responses import ResponseBase
from app.modules.materiales.material_model import TipoMaterialEnum
from app.modules.materiales.material_service import MaterialService
from app.modules.materiales.material_schema import MaterialPublicoGeneralDTO, MaterialPublicoRelacionDTO
from app.modules.resultados.resultado_service import ResultadoService
from app.modules.resultados.resultado_schema import ResultadoPublicoGeneralDTO, ResultadoPublicoFaseDTO
from app.modules.fases.fase_service import FaseService
from app.modules.fases.fase_schema import FasePublicaDTO
from app.modules.avisos.aviso_service import AvisoService
from app.modules.avisos.aviso_schema import AvisoPublicoDTO
from app.modules.convocatorias.convocatoria_service import ConvocatoriaService
from app.modules.convocatorias.convocatoria_schema import (
    ConvocatoriaIdDTO,
    ConvocatoriaInicioDTO,
    ConvocatoriaDetalleDTO,
    ConvocatoriaListPublicDTO,
    ConvocatoriaMinified
)
from app.modules.categorias.categoria_schema import CategoriaDetalleDTO
from app.modules.categorias.categoria_service import CategoriaService

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

@router.get("/materiales", response_model=PaginatedResponse[MaterialPublicoGeneralDTO])
@limiter.limit("10/minute")
def get_materiales_public(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1),
    tipo_material: Optional[TipoMaterialEnum] = Query(None),
    fecha_start: Optional[datetime] = Query(None),
    fecha_end: Optional[datetime] = Query(None),
    busqueda: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    service = MaterialService(db)
    items, total = service.get_public_materiales(page, limit, tipo_material, fecha_start, fecha_end, busqueda)
    
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    data = PaginatedData(items=items, meta=meta)
    
    return PaginatedResponse(data=data, message="Materiales obtenidos correctamente")


@router.get("/fase/{id_fase}/materiales", response_model=ResponseBase[List[MaterialPublicoRelacionDTO]])
@limiter.limit("10/minute")
def get_materiales_fase_public(
    request: Request,
    id_fase: int,
    db: Session = Depends(get_db)
):
    service = MaterialService(db)
    items = service.get_public_by_fase(id_fase)
    return ResponseBase(data=items, message="Materiales de la fase obtenidos correctamente")


@router.get("/convocatoria/{id_convocatoria}/materiales", response_model=ResponseBase[List[MaterialPublicoRelacionDTO]])
@limiter.limit("10/minute")
def get_materiales_convocatoria_public(
    request: Request,
    id_convocatoria: int,
    db: Session = Depends(get_db)
):
    service = MaterialService(db)
    items = service.get_public_by_convocatoria(id_convocatoria)
    return ResponseBase(data=items, message="Materiales de la convocatoria obtenidos correctamente")

@router.get("/resultados", response_model=PaginatedResponse[ResultadoPublicoGeneralDTO])
@limiter.limit("10/minute")
def get_resultados_finales_public(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1),
    id_convocatoria: Optional[int] = Query(None),
    id_categoria: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    service = ResultadoService(db)
    items, total = service.get_public_resultados_finales(page, limit, id_convocatoria, id_categoria)
    
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    data = PaginatedData(items=items, meta=meta)
    
    return PaginatedResponse(data=data, message="Resultados finales obtenidos correctamente")
@router.get("/fase/{id_fase}/resultados", response_model=ResponseBase[List[ResultadoPublicoFaseDTO]])
@limiter.limit("10/minute")
def get_resultados_fase_public(
    request: Request,
    id_fase: int,
    db: Session = Depends(get_db)
):
    service = ResultadoService(db)
    items = service.get_public_resultados_by_fase(id_fase)
    return ResponseBase(data=items, message="Resultados de la fase obtenidos correctamente")

@router.get("/fases/{id_categoria}", response_model=ResponseBase[List[FasePublicaDTO]])
@limiter.limit("10/minute")
def get_fases_publicas_categoria(
    id_categoria: int,
    db: Session = Depends(get_db)
):
    service = FaseService(db)
    items = service.get_fases_publicas_by_categoria(id_categoria)
    return ResponseBase(data=items, message="Fases públicas obtenidas correctamente")

@router.get("/avisos-publicos", response_model=PaginatedResponse[AvisoPublicoDTO])
@limiter.limit("10/minute")
def get_avisos_publicos(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1),
    db: Session = Depends(get_db)
):
    service = AvisoService(db)
    items, total = service.get_avisos_publicos_minified(page, limit)
    
    meta = PaginationMeta(
        page=page, 
        limit=limit, 
        total=total, 
        total_pages=(total + limit - 1) // limit
    )
    data = PaginatedData(items=items, meta=meta)
    
    return PaginatedResponse(data=data, message="Avisos públicos obtenidos correctamente")

@router.get("/convocatoria-principal", response_model=ResponseBase[ConvocatoriaIdDTO])
@limiter.limit("10/minute")
def get_public_convocatoria_principal_id(db: Session = Depends(get_db)):
    service = ConvocatoriaService(db)
    id_convocatoria = service.get_convocatoria_principal_id()
    return ResponseBase(
        data={"id_convocatoria": id_convocatoria}, 
        message="ID de convocatoria principal obtenido correctamente"
    )

@router.get("/inicio", response_model=ResponseBase[ConvocatoriaInicioDTO])
@limiter.limit("10/minute")
def get_public_inicio(db: Session = Depends(get_db)):
    service = ConvocatoriaService(db)
    data = service.get_inicio_publico()
    return ResponseBase(
        data=data, 
        message="Datos de inicio de convocatoria obtenidos correctamente"
    )

@router.get("/convocatoria/{id_convocatoria}/detalle", response_model=ResponseBase[ConvocatoriaDetalleDTO])
@limiter.limit("10/minute")
def get_public_convocatoria_detalle(id_convocatoria: int, db: Session = Depends(get_db)):
    service = ConvocatoriaService(db)
    data = service.get_detalle_publico(id_convocatoria)
    return ResponseBase(
        data=data, 
        message="Detalle de convocatoria obtenido correctamente"
    )

@router.get("/convocatorias", response_model=ResponseBase[List[ConvocatoriaListPublicDTO]])
@limiter.limit("10/minute")
def get_public_convocatorias_list(db: Session = Depends(get_db)):
    service = ConvocatoriaService(db)
    data = service.get_lista_publica()
    return ResponseBase(
        data=data, 
        message="Lista de convocatorias públicas obtenidas correctamente"
    )

@router.get("{id_convocatoria}/categorias", response_model= ResponseBase[List[CategoriaDetalleDTO]])
@limiter.limit("10/minute")
async def get_categorias_minified_lis(id_convocatoria: int, db: Session=Depends(get_db)):
    service = CategoriaService(db)
    data = service.get_by_convocatoria_minified(id_convocatoria)
    return ResponseBase(
        data= data,
        message="Lista de Caregorias Minimizada publica obtenida correctamente"
    )

@router.get("/convocatorias-minified", response_model= ResponseBase[List[ConvocatoriaMinified]])
@limiter.limit("10/minute")
async def get_convocatorias_minifed_list(db: Session = Depends(get_db)):
    service = ConvocatoriaService(db)
    data = service.get_public_minified_list()
    return ResponseBase(
        data = data,
        message= "Lista de Convocatorias Minimizada publica obtenida correctamente"
    )