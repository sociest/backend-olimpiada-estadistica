from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_admin
from app.core.responses import PaginatedData, PaginatedResponse, ResponseBase, PaginationMeta
from app.db.database import get_db
from app.modules.categorias.categoria_schema import (
    CategoriaCreateDTO,
    CategoriaEstadoUpdateDTO,
    CategoriaResponseDTO,
    CategoriaUpdateDTO,
)
from app.modules.categorias.categoria_service import CategoriaService

router = APIRouter(prefix="/categorias", tags=["categorias"])

@router.get("", response_model=PaginatedResponse[CategoriaResponseDTO])
def listar_categorias(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    service = CategoriaService(db)
    items, total = service.get_all(page=page, limit=limit)
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    data = PaginatedData(items=items, meta=meta)
    return PaginatedResponse(data=data, message="Lista de categorías obtenida correctamente")


@router.get("/convocatoria/{convocatoria_id}", response_model=PaginatedResponse[CategoriaResponseDTO])
def listar_categorias_por_convocatoria(convocatoria_id: int, page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    service = CategoriaService(db)
    items, total = service.get_by_convocatoria(convocatoria_id, page=page, limit=limit)
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    data = PaginatedData(items=items, meta=meta)
    return PaginatedResponse(data=data, message="Categorías de la convocatoria obtenidas correctamente")


@router.get("/{categoria_id}", response_model=ResponseBase[CategoriaResponseDTO])
def obtener_categoria(categoria_id: int, db: Session = Depends(get_db)):
    service = CategoriaService(db)
    categoria = service.get_by_id(categoria_id)
    return ResponseBase(data=categoria, message="Operación exitosa")


@router.post("", response_model=ResponseBase[CategoriaResponseDTO])
def crear_categoria(
    data: CategoriaCreateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = CategoriaService(db)
    categoria = service.create(data, current_admin_id)
    return ResponseBase(data=categoria, message="Categoría creada exitosamente")


@router.put("/{categoria_id}", response_model=ResponseBase[CategoriaResponseDTO])
def actualizar_categoria(
    categoria_id: int,
    data: CategoriaUpdateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = CategoriaService(db)
    categoria = service.update(categoria_id, data, current_admin_id)
    return ResponseBase(data=categoria, message="Categoría actualizada exitosamente")


@router.patch("/{categoria_id}/estado", response_model=ResponseBase[CategoriaResponseDTO])
def cambiar_estado_categoria(
    categoria_id: int,
    data: CategoriaEstadoUpdateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = CategoriaService(db)
    categoria = service.cambiar_estado(categoria_id, data, current_admin_id)
    return ResponseBase(data=categoria, message="Estado de la categoría actualizado exitosamente")


@router.delete("/{categoria_id}", response_model=ResponseBase[CategoriaResponseDTO])
def eliminar_categoria_fisica(
    categoria_id: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = CategoriaService(db)
    categoria = service.delete(categoria_id, current_admin_id)
    return ResponseBase(data=categoria, message="Categoría eliminada físicamente de forma exitosa")