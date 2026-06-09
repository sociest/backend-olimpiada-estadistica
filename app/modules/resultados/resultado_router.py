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
import os
from fastapi import APIRouter, Depends, Query, UploadFile, File
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
from app.modules.resultados.csv.schemas import AnalisisImportacionResponseDTO, ConfirmarImportacionDTO
from app.modules.resultados.csv.service import CSVImportService, ERRORS_DIR
from app.modules.resultados.csv.exporter import ExporterService
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/resultados", tags=["resultados"])


@router.get("", response_model=PaginatedResponse[ResultadoResponseDTO])
def listar_resultados(
    id_fase_prueba: int = Query(..., description="ID de la fase de prueba (obligatorio)"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    search: Optional[str] = None,
    estado_aprobacion: Optional[Literal["APROBADO", "REPROBADO"]] = None,
    sort_by: Optional[Literal["nota", "apellido"]] = None,
    sort_order: Literal["asc", "desc"] = "desc",
    db: Session = Depends(get_db)
):
    service = ResultadoService(db)
    items, total = service.get_all(id_fase_prueba, page, limit, search, estado_aprobacion, sort_by, sort_order)
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    data = PaginatedData(items=items, meta=meta)
    return PaginatedResponse(data=data, message="Lista de resultados obtenida correctamente")


@router.get("/fase/{id_fase_prueba}/aprobados", response_model=ResponseBase[list[ResultadoAprobatorioResponseDTO]])
def listar_aprobados_por_fase(
    id_fase_prueba: int,
    sort_by: Literal["nombre", "paterno", "materno", "ci", "resultado"] = "resultado",
    sort_order: Literal["asc", "desc"] = "desc",
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = ResultadoService(db)
    items = service.get_aprobados_fase(id_fase_prueba, sort_by, sort_order)
    return ResponseBase(data=items, message="Resultados aprobatorios obtenidos correctamente")


@router.get("/{resultado_id}", response_model=ResponseBase[ResultadoResponseDTO])
def obtener_resultado(resultado_id: int, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
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
    resultado = service.create(data, current_admin_id)
    return ResponseBase(data=resultado, message="Resultado creado exitosamente")


@router.post("/masivo", response_model=ResponseBase[int])
def crear_resultados_masivos(
    data: ResultadoMasivoCreateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = ResultadoService(db)
    creados = service.create_masivo(data, current_admin_id)
    return ResponseBase(data=creados, message=f"{creados} resultados creados masivamente en borrador")


@router.put("/masivo", response_model=ResponseBase[int])
def actualizar_resultados_masivos(
    data: ResultadoMasivoUpdateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = ResultadoService(db)
    actualizados = service.update_masivo(data, current_admin_id)
    return ResponseBase(data=actualizados, message=f"{actualizados} resultados actualizados masivamente")


@router.put("/{resultado_id}", response_model=ResponseBase[ResultadoResponseDTO])
def actualizar_resultado(
    resultado_id: int,
    data: ResultadoUpdateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = ResultadoService(db)
    resultado = service.update(resultado_id, data, current_admin_id)
    return ResponseBase(data=resultado, message="Resultado actualizado exitosamente")


@router.patch("/{resultado_id}/estado", response_model=ResponseBase[ResultadoResponseDTO])
def cambiar_estado_resultado_individual(
    resultado_id: int,
    data: ResultadoEstadoUpdateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = ResultadoService(db)
    resultado = service.cambiar_estado_individual(resultado_id, data, current_admin_id)
    return ResponseBase(data=resultado, message="Estado del resultado actualizado")


@router.put("/fase/{id_fase_prueba}/publicar", response_model=ResponseBase[int])
def publicar_resultados_fase(
    id_fase_prueba: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = ResultadoService(db)
    modificados = service.publicar_fase(id_fase_prueba, current_admin_id)
    return ResponseBase(data=modificados, message="Resultados de la fase publicados correctamente")


@router.put("/fase/{id_fase_prueba}/ocultar", response_model=ResponseBase[int])
def ocultar_resultados_fase(
    id_fase_prueba: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = ResultadoService(db)
    modificados = service.ocultar_fase(id_fase_prueba, current_admin_id)
    return ResponseBase(data=modificados, message="Resultados de la fase ocultados correctamente")

@router.post("/import-csv/analizar/{id_fase_prueba}", response_model=ResponseBase[AnalisisImportacionResponseDTO])
async def analizar_csv_fase(
    id_fase_prueba: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = CSVImportService(db)
    analisis = await service.analizar_csv(id_fase_prueba, archivo)
    return ResponseBase(data=analisis, message="CSV analizado correctamente.")

@router.post("/import-csv/{id_fase_prueba}", response_model=ResponseBase[dict])
def importar_csv_definitivo(
    id_fase_prueba: int,
    payload: ConfirmarImportacionDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = CSVImportService(db)
    resultado = service.procesar_importacion(id_fase_prueba, payload, current_admin_id)
    return ResponseBase(data=resultado, message="Importación masiva completada correctamente.")

@router.get("/import-csv/download/{filename}")
def descargar_csv_errores(
    filename: str, 
    current_admin_id: int = Depends(get_current_admin)
):
    ruta_archivo = os.path.join(ERRORS_DIR, filename)
    if not os.path.exists(ruta_archivo):
        raise NotFoundError("Archivo de errores no encontrado o expirado.")
    
    return FileResponse(
        path=ruta_archivo, 
        filename=filename, 
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/export/csv/{id_fase_prueba}")
def exportar_fase_csv(
    id_fase_prueba: int,
    estado_aprobacion: Literal["APROBADO", "REPROBADO", "TODOS"] = "TODOS",
    incluir_nombres: bool = False,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = ExporterService(db)
    archivo_csv = service.export_csv(id_fase_prueba, estado_aprobacion, incluir_nombres)
    
    return StreamingResponse(
        iter([archivo_csv.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=resultados_fase_{id_fase_prueba}.csv"}
    )

@router.get("/export/pdf/{id_fase_prueba}")
def exportar_fase_pdf(
    id_fase_prueba: int,
    estado_aprobacion: Literal["APROBADO", "REPROBADO", "TODOS"] = "TODOS",
    incluir_nombres: bool = False,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = ExporterService(db)
    archivo_pdf = service.export_pdf(id_fase_prueba, estado_aprobacion, incluir_nombres)
    
    return StreamingResponse(
        archivo_pdf, 
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=resultados_fase_{id_fase_prueba}.pdf"}
    )
