from typing import Literal, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin
from app.core.responses import PaginatedData, PaginatedResponse, ResponseBase, PaginationMeta
from app.db.database import get_db
from app.modules.resultados.resultado_schema import (
    ResultadoAprobatorioResponseDTO,
    ResultadoCreateDTO,
    ResultadoEstadoUpdateDTO,
    ResultadoMasivoCreateDTO,
    ResultadoMasivoUpdateDTO,
    ResultadoResponseDTO,
    ResultadoUpdateDTO
)
from app.modules.resultados.resultado_service import ResultadoService


router = APIRouter(prefix="/resultados", tags=["resultados"])


@router.get("", response_model=PaginatedResponse[ResultadoResponseDTO])
def listar_resultados(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    search: Optional[str] = None,
    estado_aprobacion: Optional[Literal["APROBADO", "REPROBADO"]] = None,
    sort_by: Optional[Literal["nota", "apellido"]] = None,
    sort_order: Literal["asc", "desc"] = "desc",
    db: Session = Depends(get_db)
):
    service = ResultadoService(db)
    items, total = service.get_all(page, limit, search, estado_aprobacion, sort_by, sort_order)
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    data = PaginatedData(items=items, meta=meta)
    return PaginatedResponse(data=data, message="Lista de resultados obtenida correctamente")


@router.get("/fase/{id_fase_prueba}/aprobados", response_model=ResponseBase[list[ResultadoAprobatorioResponseDTO]])
def listar_aprobados_por_fase(
    id_fase_prueba: int,
    sort_by: Literal["nombre", "paterno", "materno", "ci", "resultado"] = "resultado",
    sort_order: Literal["asc", "desc"] = "desc",
    db: Session = Depends(get_db)
):
    service = ResultadoService(db)
    items = service.get_aprobados_fase(id_fase_prueba, sort_by, sort_order)
    return ResponseBase(data=items, message="Resultados aprobatorios obtenidos correctamente")


@router.get("/{resultado_id}", response_model=ResponseBase[ResultadoResponseDTO])
def obtener_resultado(resultado_id: int, db: Session = Depends(get_db)):
    service = ResultadoService(db)
    resultado = service.get_by_id(resultado_id)
    return ResponseBase(data=resultado, message="Operación exitosa")


@router.post("", response_model=ResponseBase[ResultadoResponseDTO])
def crear_resultado(
    data: ResultadoCreateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = ResultadoService(db)
    resultado = service.create(data)
    return ResponseBase(data=resultado, message="Resultado creado exitosamente")


@router.post("/masivo", response_model=ResponseBase[int])
def crear_resultados_masivos(
    data: ResultadoMasivoCreateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = ResultadoService(db)
    creados = service.create_masivo(data)
    return ResponseBase(data=creados, message=f"{creados} resultados creados masivamente en borrador")


@router.put("/masivo", response_model=ResponseBase[int])
def actualizar_resultados_masivos(
    data: ResultadoMasivoUpdateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = ResultadoService(db)
    actualizados = service.update_masivo(data)
    return ResponseBase(data=actualizados, message=f"{actualizados} resultados actualizados masivamente")


@router.put("/{resultado_id}", response_model=ResponseBase[ResultadoResponseDTO])
def actualizar_resultado(
    resultado_id: int,
    data: ResultadoUpdateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = ResultadoService(db)
    resultado = service.update(resultado_id, data)
    return ResponseBase(data=resultado, message="Resultado actualizado exitosamente")


@router.patch("/{resultado_id}/estado", response_model=ResponseBase[ResultadoResponseDTO])
def cambiar_estado_resultado_individual(
    resultado_id: int,
    data: ResultadoEstadoUpdateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = ResultadoService(db)
    resultado = service.cambiar_estado_individual(resultado_id, data)
    return ResponseBase(data=resultado, message="Estado del resultado actualizado")


@router.put("/fase/{id_fase_prueba}/publicar", response_model=ResponseBase[int])
def publicar_resultados_fase(
    id_fase_prueba: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = ResultadoService(db)
    modificados = service.publicar_fase(id_fase_prueba)
    return ResponseBase(data=modificados, message="Resultados de la fase publicados correctamente")


@router.put("/fase/{id_fase_prueba}/ocultar", response_model=ResponseBase[int])
def ocultar_resultados_fase(
    id_fase_prueba: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = ResultadoService(db)
    modificados = service.ocultar_fase(id_fase_prueba)
    return ResponseBase(data=modificados, message="Resultados de la fase ocultados correctamente")