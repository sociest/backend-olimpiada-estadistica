from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin
from app.core.responses import PaginatedData, PaginatedResponse, PaginationMeta, ResponseBase
from app.db.database import get_db
from app.modules.convocatorias.convocatoria_schema import (
    ConvocatoriaCreateDTO,
    ConvocatoriaResponseDTO,
    ConvocatoriaUpdateDTO,
)
from app.modules.convocatorias.convocatoria_service import ConvocatoriaService


router = APIRouter(prefix="/convocatorias", tags=["convocatorias"])


@router.get("", response_model=PaginatedResponse[ConvocatoriaResponseDTO])
def listar_convocatorias(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    service = ConvocatoriaService(db)
    items, total = service.get_all(page=page, limit=limit)
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    data = PaginatedData(items=items, meta=meta)
    return PaginatedResponse(data=data, message="Lista obtenida correctamente")


@router.get("/{convocatoria_id}", response_model=ResponseBase[ConvocatoriaResponseDTO])
def obtener_convocatoria(convocatoria_id: int, db: Session = Depends(get_db)):
    service = ConvocatoriaService(db)
    convocatoria = service.get_by_id(convocatoria_id)
    return ResponseBase(data=convocatoria, message="Operacion exitosa")


@router.post("", response_model=ResponseBase[ConvocatoriaResponseDTO])
def crear_convocatoria(
    data: ConvocatoriaCreateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = ConvocatoriaService(db)
    convocatoria = service.create(data)
    return ResponseBase(data=convocatoria, message="Operacion exitosa")


@router.put("/{convocatoria_id}", response_model=ResponseBase[ConvocatoriaResponseDTO])
def actualizar_convocatoria(
    convocatoria_id: int,
    data: ConvocatoriaUpdateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = ConvocatoriaService(db)
    convocatoria = service.update(convocatoria_id, data)
    return ResponseBase(data=convocatoria, message="Operacion exitosa")


@router.post("/{convocatoria_id}/publicar", response_model=ResponseBase[ConvocatoriaResponseDTO])
def publicar_convocatoria(convocatoria_id: int, db: Session = Depends(get_db)):
    service = ConvocatoriaService(db)
    convocatoria = service.publish(convocatoria_id)
    return ResponseBase(data=convocatoria, message="Operacion exitosa")


@router.delete("/{convocatoria_id}", response_model=ResponseBase[ConvocatoriaResponseDTO])
def eliminar_convocatoria(
    convocatoria_id: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = ConvocatoriaService(db)
    convocatoria = service.get_by_id(convocatoria_id)
    service.delete(convocatoria_id)
    return ResponseBase(data=convocatoria, message="Operacion exitosa")
