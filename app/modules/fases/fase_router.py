from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_admin
from app.core.responses import PaginatedData, PaginatedResponse, PaginationMeta, ResponseBase
from app.db.database import get_db
from app.modules.fases.fase_schema import (
    FaseEstadoUpdateDTO,
    FaseMinifiedResponseDTO,
    FasePreparacionCreateDTO,
    FasePreparacionResponseDTO,
    FasePreparacionUpdateDTO,
    FasePruebaCreateDTO,
    FasePruebaResponseDTO,
    FasePruebaUpdateDTO,
    FaseResponsePolymorphic,
)
from app.modules.fases.fase_service import FaseService

router = APIRouter(prefix="/fases", tags=["fases"])

@router.get("", response_model=PaginatedResponse[FaseResponsePolymorphic])
def listar_fases(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    service = FaseService(db)
    items, total = service.get_all(page=page, limit=limit)
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    data = PaginatedData(items=items, meta=meta)
    return PaginatedResponse(data=data, message="Lista de fases obtenida correctamente")

@router.get("/{fase_id}", response_model=ResponseBase[FaseResponsePolymorphic])
def obtener_fase(fase_id: int, db: Session = Depends(get_db)):
    service = FaseService(db)
    fase = service.get_by_id(fase_id)
    return ResponseBase(data=fase, message="Fase obtenida exitosamente")

@router.get("/categoria/{categoria_id}", response_model=PaginatedResponse[FaseResponsePolymorphic])
def listar_fases_por_categoria(
    categoria_id: int,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    service = FaseService(db)
    items = service.get_by_id_categoria(categoria_id)
    meta = PaginationMeta(page=page, limit=limit, total=len(items), total_pages=(len(items) + limit - 1) // limit)
    data = PaginatedData(items=items, meta=meta)
    return PaginatedResponse(data=data, message="Lista de fases obtenida correctamente")

@router.get("/prueba/{categoria_id}/minified", response_model=ResponseBase[List[FaseMinifiedResponseDTO]])
def listar_fases_prueba_minified(categoria_id: int, db: Session = Depends(get_db)):
    service = FaseService(db)
    data = service.get_pruebas_minified_by_categoria(categoria_id)
    return ResponseBase(data=data, message="Lista minimizada de fases de prueba obtenida exitosamente")

@router.post("/prueba", response_model=ResponseBase[FasePruebaResponseDTO])
def crear_fase_prueba(
    data: FasePruebaCreateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = FaseService(db)
    resultado = service.create_fase_prueba(data, current_admin_id)
    return ResponseBase(data=resultado, message="Fase de Prueba creada exitosamente")

@router.put("/prueba/{fase_id}", response_model=ResponseBase[FasePruebaResponseDTO])
def actualizar_fase_prueba(
    fase_id: int,
    data: FasePruebaUpdateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = FaseService(db)
    fase = service.update_fase_prueba(fase_id, data, current_admin_id)
    return ResponseBase(data=fase, message="Fase de Prueba actualizada exitosamente")

@router.post("/preparacion", response_model=ResponseBase[FasePreparacionResponseDTO])
def crear_fase_preparacion(
    data: FasePreparacionCreateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = FaseService(db)
    resultado = service.create_fase_preparacion(data, current_admin_id)
    return ResponseBase(data=resultado, message="Fase de Preparación creada exitosamente")

@router.put("/preparacion/{fase_id}", response_model=ResponseBase[FasePreparacionResponseDTO])
def actualizar_fase_preparacion(
    fase_id: int,
    data: FasePreparacionUpdateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = FaseService(db)
    fase = service.update_fase_preparacion(fase_id, data, current_admin_id)
    return ResponseBase(data=fase, message="Fase de Preparación actualizada exitosamente")

@router.patch("/{fase_id}/estado", response_model=ResponseBase[FaseResponsePolymorphic])
def cambiar_estado_fase(
    fase_id: int,
    data: FaseEstadoUpdateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = FaseService(db)
    fase = service.cambiar_estado(fase_id, data, current_admin_id)
    return ResponseBase(data=fase, message="Estado de la fase actualizado exitosamente")

@router.patch("/{fase_id}", response_model=ResponseBase[FaseResponsePolymorphic])
def eliminar_fase_logica(
    fase_id: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = FaseService(db)
    fase = service.baja_logica(fase_id, current_admin_id)
    return ResponseBase(data=fase, message="Fase dada de baja correctamente")

@router.delete("/{fase_id}")
def eliminar_fase(
    fase_id: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = FaseService(db)
    service.eliminar_fase(fase_id, current_admin_id)
    return ResponseBase(data={}, message="Fase eliminada correctamente")