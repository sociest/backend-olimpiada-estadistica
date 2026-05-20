from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.responses import PaginatedData, PaginatedResponse, PaginationMeta, ResponseBase
from app.db.database import get_db
from app.modules.avisos.aviso_service import AvisoService
from app.modules.categorias.categoria_service import CategoriaService
from app.modules.convocatorias.convocatoria_service import ConvocatoriaService
from app.modules.fases.fase_schema import FaseResponseDTO
from app.modules.fases.fase_service import FaseService
from app.modules.materiales.material_service import MaterialService
from app.modules.personas.persona_service import PersonaService
from app.modules.public_bff.public_schema import ConvocatoriaDetalleDTO, InicioResponseDTO, MaterialPublicoSimpleDTO
from app.modules.public_bff.public_service import PublicBffService


router = APIRouter(prefix="/public", tags=["public"])


def _get_service(db: Session) -> PublicBffService:
    return PublicBffService(
        convocatoria_service=ConvocatoriaService(db),
        categoria_service=CategoriaService(db),
        aviso_service=AvisoService(db),
        material_service=MaterialService(db),
        fase_service=FaseService(db),
        persona_service=PersonaService(db),
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


@router.get("/categorias/{categoria_id}/fases", response_model=ResponseBase[list[FaseResponseDTO]])
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
