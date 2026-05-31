from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session
import os
from fastapi.responses import FileResponse
from typing import Optional

from app.core.dependencies import get_current_admin
from app.core.exceptions import NotFoundError
from app.core.responses import PaginatedData, PaginatedResponse, PaginationMeta, ResponseBase
from app.db.database import get_db
from app.modules.colegios.colegio_model import EstadoColegio, TipoColegio, TurnoColegio
from app.modules.colegios.colegio_schema import ColegioCreateDTO, ColegioResponseDTO, ColegioUpdateDTO, ColegioDetailResponseDTO
from app.modules.colegios.colegio_service import ColegioService
from app.modules.colegios.colegio_schema import CSVImportDBResponseDTO, CSVUploadResponseDTO, ColegioCSVImportDTO
from app.modules.colegios.csv.service import generar_csv_errores, obtener_csv_error_path

router = APIRouter(prefix="/colegios", tags=["colegios"])


@router.get("", response_model=PaginatedResponse[ColegioResponseDTO])
def listar_colegios(
    page: int = 1, limit: int = 10,
    nombre: Optional[str] = None,
    municipio: Optional[str] = None,
    estado: Optional[EstadoColegio] = None,
    tipo: Optional[TipoColegio] = None,
    turno: Optional[TurnoColegio] = None,
    director_nombre: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = ColegioService(db)
    filters = {
        "nombre": nombre, "municipio": municipio, "estado": estado,
        "tipo": tipo, "turno": turno, "director_nombre": director_nombre
    }
    items, total = service.get_all(page=page, limit=limit, filters=filters)
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    data = PaginatedData(items=items, meta=meta)
    return PaginatedResponse(data=data, message="Lista obtenida correctamente")

@router.get("/{colegio_id}", response_model=ResponseBase[ColegioDetailResponseDTO])
def obtener_colegio(colegio_id: int, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = ColegioService(db)
    colegio = service.get_by_id(colegio_id)
    return ResponseBase(data=colegio, message="Operacion exitosa")

@router.post("", response_model=ResponseBase[ColegioResponseDTO])
def crear_colegio(
    data: ColegioCreateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = ColegioService(db)
    colegio = service.create(data, current_admin_id)
    return ResponseBase(data=colegio, message="Operacion exitosa")


@router.put("/{colegio_id}", response_model=ResponseBase[ColegioResponseDTO])
def actualizar_colegio(
    colegio_id: int,
    data: ColegioUpdateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = ColegioService(db)
    colegio = service.update(colegio_id, data, current_admin_id)
    return ResponseBase(data=colegio, message="Operacion exitosa")

@router.patch("/{colegio_id}/baja", response_model=ResponseBase[ColegioResponseDTO])
def baja_logica_colegio(colegio_id: int, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = ColegioService(db)
    colegio = service.delete_logic(colegio_id, current_admin_id)
    return ResponseBase(data=colegio, message="Colegio dado de baja lógicamente (INACTIVO)")


@router.patch("/{colegio_id}/alta", response_model=ResponseBase[ColegioResponseDTO])
def alta_logica_colegio(colegio_id: int, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = ColegioService(db)
    colegio = service.alta_logic(colegio_id, current_admin_id)
    return ResponseBase(data=colegio, message="Colegio dado de alta logicamente (REVISADO)")


@router.delete("/{colegio_id}", response_model=ResponseBase[dict])
def eliminar_colegio_total(colegio_id: int, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = ColegioService(db)
    service.delete_total(colegio_id, current_admin_id)
    return ResponseBase(data={}, message="Colegio eliminado permanentemente")


@router.post("/subir-csv", response_model=ResponseBase[CSVUploadResponseDTO])
def subir_csv_colegios(
    departamento: str = Form(...),
    file: UploadFile = File(...), 
    db: Session = Depends(get_db), 
    current_admin_id: int = Depends(get_current_admin)
):
    service = ColegioService(db)
    resultado = service.parse_csv_file(file=file.file, departamento=departamento)
    csv_errores_path = generar_csv_errores(resultado.filas_error_csv)
    response = CSVUploadResponseDTO(
        total_validos=len(resultado.validos),
        total_errores=len(resultado.errores), 
        validos=resultado.validos, 
        errores=resultado.errores, 
        filas_error_csv=resultado.filas_error_csv, 
        csv_errores_url=(
                f"/colegios/csv-error/"
                f"{os.path.basename(csv_errores_path)}"
            )
            if csv_errores_path else None
        )
    
    
    return ResponseBase(data=response, message="CSV procesado correctamente")

@router.get("/csv-error/{filename}")
def descargar_csv_error(
    filename: str,
    current_admin_id: int = Depends(get_current_admin),
):
    filepath = obtener_csv_error_path(
        filename
    )

    if not os.path.exists(filepath):
        raise NotFoundError(
            "Archivo CSV no encontrado"
        )

    return FileResponse(
        path=filepath,
        media_type="text/csv",
        filename=filename
    )

@router.post("/csv", response_model=ResponseBase[CSVImportDBResponseDTO])
def importar_colegios_csv(
    colegios: list[ColegioCSVImportDTO],
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = ColegioService(db)
    resultado = service.import_from_csv(colegios, current_admin_id)
    response = CSVImportDBResponseDTO(insertados=resultado["insertados"], errores=resultado["errores"])
    return ResponseBase(data=response, message="Importación completada")
