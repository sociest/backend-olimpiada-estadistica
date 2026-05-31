from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_admin, limiter, verify_bot_protection
from app.core.responses import PaginatedData, PaginatedResponse, PaginationMeta, ResponseBase
from app.db.database import get_db
from app.modules.inscripciones.inscripcion_schema import (
    InscripcionFormularioDTO, InscripcionFormularioRequestDTO, InscripcionFormularioResponseDTO,
    InscripcionResponseDTO, EstudianteBuscarRequestDTO, EstudianteBusquedaResponseDTO,
    InscripcionAdminCreateDTO, InscripcionEstadoUpdateDTO, ExportarInscripcionesRequestDTO
)
from app.modules.inscripciones.inscripcion_service import InscripcionService
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/inscripciones", tags=["inscripciones"])

@router.post("/formulario", response_model=ResponseBase[InscripcionFormularioResponseDTO])
@limiter.limit("5/minute")
async def registrar_inscripcion_formulario(
    request: Request, data: InscripcionFormularioRequestDTO, db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else None
    await verify_bot_protection(data.cf_turnstile_response, data.username_hp, client_ip)
    clean_data = InscripcionFormularioDTO(**data.model_dump(exclude={"username_hp", "cf_turnstile_response"}))
    service = InscripcionService(db)
    resultado = service.registrar_formulario(clean_data)
    return ResponseBase(data=resultado, message="Inscripción registrada correctamente")

@router.post("/verificar-estudiante", response_model=ResponseBase[EstudianteBusquedaResponseDTO])
@limiter.limit("5/minute")
async def verificar_estudiante_existente(
    request: Request, data: EstudianteBuscarRequestDTO, db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else None
    await verify_bot_protection(data.cf_turnstile_response, data.username_hp, client_ip)
    service = InscripcionService(db)
    resultado = service.buscar_estudiante_registro(data.carnet_identidad, data.fecha_nacimiento)
    return ResponseBase(data=resultado, message="Verificación de estudiante completada")

@router.get("", response_model=PaginatedResponse[InscripcionResponseDTO])
def listar_inscripciones_panel(
    page: int = 1,
    limit: int = 10,
    id_colegio: Optional[int] = Query(None),
    id_categoria: Optional[int] = Query(None),
    estado: Optional[str] = Query(None),
    search_nombre: Optional[str] = Query(None),
    search_documento: Optional[str] = Query(None),
    fecha_inicio: Optional[datetime] = Query(None),
    fecha_fin: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = InscripcionService(db)
    items, total = service.list_all(
        page=page, limit=limit, id_colegio=id_colegio, id_categoria=id_categoria, estado=estado,
        search_nombre=search_nombre, search_documento=search_documento, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin
    )
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    data = PaginatedData(items=items, meta=meta)
    return PaginatedResponse(data=data, message="Inscripciones recuperadas exitosamente")

@router.get("/{inscripcion_id}", response_model=ResponseBase[InscripcionResponseDTO])
def obtener_inscripcion_por_id(inscripcion_id: int, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = InscripcionService(db)
    inscripcion = service.obtener_por_id(inscripcion_id)
    return ResponseBase(data=inscripcion, message="Detalle de inscripción obtenido")

@router.post("/admin", response_model=ResponseBase[InscripcionResponseDTO])
def crear_inscripcion_manual_admin(data: InscripcionAdminCreateDTO, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = InscripcionService(db)
    nueva_ins = service.crear_inscripcion_admin(data, current_admin_id)
    return ResponseBase(data=nueva_ins, message="Inscripción creada manualmente por administrador")

@router.patch("/{inscripcion_id}/estado", response_model=ResponseBase[InscripcionResponseDTO])
def cambiar_estado_inscripcion(inscripcion_id: int, data: InscripcionEstadoUpdateDTO, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = InscripcionService(db)
    inscripcion_act = service.actualizar_estado(inscripcion_id, data, current_admin_id)
    return ResponseBase(data=inscripcion_act, message=f"Inscripción actualizada a estado {data.estado}")

@router.delete("/{inscripcion_id}", response_model=ResponseBase[dict])
def eliminar_inscripcion(inscripcion_id: int, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = InscripcionService(db)
    service.eliminar_inscripcion(inscripcion_id, current_admin_id)
    return ResponseBase(data={}, message="Inscripción eliminada correctamente del registro")

@router.post("/exportar/csv")
def exportar_inscripciones_a_csv(
    data: ExportarInscripcionesRequestDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = InscripcionService(db)
    buffer = service.exportar_csv(data.id_inscripciones)
    headers = {
        'Content-Disposition': 'attachment; filename="estudiantes_seleccionados.csv"'
    }
    return StreamingResponse(buffer, media_type="text/csv", headers=headers)


@router.post("/exportar/pdf")
def exportar_inscripciones_a_pdf(
    data: ExportarInscripcionesRequestDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = InscripcionService(db)
    buffer = service.exportar_pdf(data.id_inscripciones)
    headers = {
        'Content-Disposition': 'attachment; filename="estudiantes_seleccionados.pdf"'
    }
    return StreamingResponse(buffer, media_type="application/pdf", headers=headers)