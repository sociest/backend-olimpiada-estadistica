from typing import Optional
from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io
from app.core.dependencies import get_current_admin, limiter, verify_bot_protection
from app.core.responses import PaginatedData, PaginatedResponse, PaginationMeta, ResponseBase
from app.db.database import get_db
from app.modules.estudiantes.estudiante_schema import (
    EstudianteCreateDTO, EstudianteResponseDTO, EstudianteUpdateDTO, 
    EstudianteEstadoUpdateDTO, ExportarEstudiantesDTO
)
from app.modules.estudiantes.estudiante_service import EstudianteService
from app.modules.categorias.categoria_model import NivelEducativo

router = APIRouter(prefix="/estudiantes", tags=["estudiantes"])

@router.post("/", response_model=ResponseBase[EstudianteResponseDTO])
def crear_estudiante(data: EstudianteCreateDTO, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = EstudianteService(db)
    estudiante = service.crear_estudiante(data, current_admin_id)
    return ResponseBase(data=estudiante, message="Estudiante creado con éxito")

@router.get("/", response_model=PaginatedResponse[EstudianteResponseDTO])
def listar_estudiantes(
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = Query(None),
    carnet: Optional[str] = Query(None),
    telefono: Optional[str] = Query(None),
    rude: Optional[str] = Query(None),
    mes_nacimiento: Optional[int] = Query(None),
    anio_nacimiento: Optional[int] = Query(None),
    nivel: Optional[NivelEducativo] = Query(None),
    curso: Optional[int] = Query(None),
    id_colegio: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = EstudianteService(db)
    items, total = service.listar_estudiantes(
        page, limit, search=search, carnet=carnet, telefono=telefono, rude=rude, 
        mes_nacimiento=mes_nacimiento, anio_nacimiento=anio_nacimiento, 
        nivel=nivel, curso=curso, id_colegio=id_colegio
    )
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    data = PaginatedData(items=items, meta=meta)
    return PaginatedResponse(data=data, message="Lista obtenida correctamente")

@router.get("/{estudiante_id}", response_model=ResponseBase[EstudianteResponseDTO])
def obtener_estudiante(estudiante_id: int, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = EstudianteService(db)
    estudiante = service.obtener_por_id(estudiante_id)
    return ResponseBase(data=estudiante, message="Estudiante encontrado")

@router.patch("/{estudiante_id}", response_model=ResponseBase[EstudianteResponseDTO])
def actualizar_estudiante(estudiante_id: int, data: EstudianteUpdateDTO, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = EstudianteService(db)
    estudiante = service.actualizar_estudiante(estudiante_id, data, current_admin_id)
    return ResponseBase(data=estudiante, message="Estudiante actualizado")

@router.patch("/{estudiante_id}/estado", response_model=ResponseBase[EstudianteResponseDTO])
def cambiar_estado_estudiante(estudiante_id: int, data: EstudianteEstadoUpdateDTO, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = EstudianteService(db)
    estudiante = service.cambiar_estado(estudiante_id, data, current_admin_id)
    return ResponseBase(data=estudiante, message="Estado actualizado (Alta/Baja)")

@router.post("/exportar/csv")
def exportar_csv(data: ExportarEstudiantesDTO, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = EstudianteService(db)
    csv_content = service.exportar_csv(data.ids)
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=estudiantes.csv"}
    )

@router.post("/exportar/pdf")
def exportar_pdf(data: ExportarEstudiantesDTO, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = EstudianteService(db)
    pdf_content = service.exportar_pdf(data.ids)
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=estudiantes.pdf"}
    )
