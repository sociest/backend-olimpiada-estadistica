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
    mapped = []
    for item in items:
        data_item = item.__dict__.copy()
        data_item.pop("_sa_instance_state", None)
        data_item["estado_temporal"] = service.calculate_estado_temporal(item)
        mapped.append(data_item)
    data = PaginatedData(items=mapped, meta=meta)
    return PaginatedResponse(data=data, message="Lista obtenida correctamente")


@router.get("/{convocatoria_id}", response_model=ResponseBase[ConvocatoriaResponseDTO])
def obtener_convocatoria(convocatoria_id: int, db: Session = Depends(get_db)):
    service = ConvocatoriaService(db)
    convocatoria = service.get_by_id(convocatoria_id)
    data = convocatoria.__dict__.copy()
    data.pop("_sa_instance_state", None)
    data["estado_temporal"] = service.calculate_estado_temporal(convocatoria)
    return ResponseBase(data=data, message="Operacion exitosa")


@router.post("", response_model=ResponseBase[ConvocatoriaResponseDTO])
def crear_convocatoria(
    data: ConvocatoriaCreateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = ConvocatoriaService(db)
    convocatoria = service.create(data)
    data_out = convocatoria.__dict__.copy()
    data_out.pop("_sa_instance_state", None)
    data_out["estado_temporal"] = service.calculate_estado_temporal(convocatoria)
    return ResponseBase(data=data_out, message="Operacion exitosa")


@router.put("/{convocatoria_id}", response_model=ResponseBase[ConvocatoriaResponseDTO])
def actualizar_convocatoria(
    convocatoria_id: int,
    data: ConvocatoriaUpdateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = ConvocatoriaService(db)
    convocatoria = service.update(convocatoria_id, data)
    data_out = convocatoria.__dict__.copy()
    data_out.pop("_sa_instance_state", None)
    data_out["estado_temporal"] = service.calculate_estado_temporal(convocatoria)
    return ResponseBase(data=data_out, message="Operacion exitosa")


@router.post("/{convocatoria_id}/publicar", response_model=ResponseBase[ConvocatoriaResponseDTO])
def publicar_convocatoria(convocatoria_id: int, db: Session = Depends(get_db)):
    service = ConvocatoriaService(db)
    convocatoria = service.publish(convocatoria_id)
    data_out = convocatoria.__dict__.copy()
    data_out.pop("_sa_instance_state", None)
    data_out["estado_temporal"] = service.calculate_estado_temporal(convocatoria)
    return ResponseBase(data=data_out, message="Operacion exitosa")


@router.delete("/{convocatoria_id}", response_model=ResponseBase[ConvocatoriaResponseDTO])
def eliminar_convocatoria(
    convocatoria_id: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = ConvocatoriaService(db)
    convocatoria = service.get_by_id(convocatoria_id)
    service.delete(convocatoria_id)
    data_out = convocatoria.__dict__.copy()
    data_out.pop("_sa_instance_state", None)
    data_out["estado_temporal"] = service.calculate_estado_temporal(convocatoria)
    return ResponseBase(data=data_out, message="Operacion exitosa")
