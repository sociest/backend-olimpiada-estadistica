from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin
from app.core.responses import PaginatedData, PaginatedResponse, PaginationMeta, ResponseBase
from app.db.database import get_db
from app.modules.inscripciones.inscripcion_schema import (
    InscripcionFormularioDTO,
    InscripcionFormularioResponseDTO,
    InscripcionResponseDTO,
    EstudianteBuscarDTO,
    EstudianteBusquedaResponseDTO,
)
from app.modules.inscripciones.inscripcion_service import InscripcionService


router = APIRouter(prefix="/inscripciones", tags=["inscripciones"])


@router.post("/formulario", response_model=ResponseBase[InscripcionFormularioResponseDTO])
def registrar_inscripcion_formulario(data: InscripcionFormularioDTO, db: Session = Depends(get_db)):
    service = InscripcionService(db)
    resultado = service.registrar_formulario(data)
    return ResponseBase(data=resultado, message="Inscripcion registrada correctamente")


@router.get("", response_model=PaginatedResponse[InscripcionResponseDTO])
def listar_inscripciones(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = InscripcionService(db)
    items, total = service.list_all(page=page, limit=limit)
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    data = PaginatedData(items=items, meta=meta)
    return PaginatedResponse(data=data, message="Lista obtenida correctamente")

@router.post("/verificar-estudiante", response_model=ResponseBase[EstudianteBusquedaResponseDTO])
def verificar_estudiante_existente(data: EstudianteBuscarDTO, db: Session = Depends(get_db)):
    service = InscripcionService(db)
    resultado = service.buscar_estudiante_registro(data.carnet_identidad, data.fecha_nacimiento)
    return ResponseBase(data=resultado, message="Estudiante localizado con éxito")