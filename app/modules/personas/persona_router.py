from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin
from app.core.responses import PaginatedData, PaginatedResponse, PaginationMeta, ResponseBase
from app.db.database import get_db
from typing import Optional
from app.modules.personas.persona_model import EstadoPersona, TipoColaborador
from app.modules.personas.persona_schema import (
    ColaboradorCreateDTO,
    ColaboradorResponseDTO,
    ColaboradorUpdateDTO,
    DirectorCreateDTO,
    DirectorResponseDTO,
    DirectorUpdateDTO,
    DirectorMinifiedDTO
)
from app.modules.personas.persona_service import PersonaService


router = APIRouter(prefix="/personas", tags=["personas"])

@router.get("/directores", response_model=PaginatedResponse[DirectorResponseDTO])
def listar_directores(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    service = PersonaService(db)
    items, total = service.list_directores(page=page, limit=limit)
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    data = PaginatedData(items=items, meta=meta)
    return PaginatedResponse(data=data, message="Lista obtenida correctamente")

@router.post("/directores", response_model=ResponseBase[DirectorResponseDTO])
def crear_director(
    data: DirectorCreateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = PersonaService(db)
    director = service.create_director(data, current_admin_id)
    return ResponseBase(data=director, message="Operacion exitosa")

@router.get("/directores/lista-corta", response_model=ResponseBase[list[DirectorMinifiedDTO]])
def listar_directores_corta(db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = PersonaService(db)
    items = service.list_directores_minified()
    return ResponseBase(data=items, message="Lista minificada obtenida exitosamente")

@router.get("/directores/{director_id}", response_model=ResponseBase[DirectorResponseDTO])
def obtener_director(director_id: int, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = PersonaService(db)
    director, persona = service.get_director_by_id(director_id)
    data = service._format_director_response(director, persona)
    return ResponseBase(data=data, message="Operacion exitosa")

@router.put("/directores/{director_id}", response_model=ResponseBase[DirectorResponseDTO])
def actualizar_director(director_id: int, data: DirectorUpdateDTO, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = PersonaService(db)
    director = service.update_director(director_id, data, current_admin_id)
    return ResponseBase(data=director, message="Director actualizado correctamente")

@router.patch("/directores/{director_id}/baja", response_model=ResponseBase[DirectorResponseDTO])
def baja_logica_director(director_id: int, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = PersonaService(db)
    director = service.delete_director_logic(director_id, current_admin_id)
    return ResponseBase(data=director, message="Director dado de baja lógicamente")

@router.delete("/directores/{director_id}", response_model=ResponseBase[dict])
def eliminar_director_total(director_id: int, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = PersonaService(db)
    service.delete_director_total(director_id, current_admin_id)
    return ResponseBase(data={}, message="Director eliminado permanentemente")

@router.patch("/directores/{director_id}/alta", response_model=ResponseBase[DirectorResponseDTO])
def alta_logica_director(director_id: int, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = PersonaService(db)
    director = service.alta_director_logic(director_id, current_admin_id)
    return ResponseBase(data=director, message="Director dado de alta logicamente")
@router.get("/colaboradores", response_model=PaginatedResponse[ColaboradorResponseDTO])
def listar_colaboradores(
    page: int = 1, 
    limit: int = 10,
    nombre: Optional[str] = Query(None),
    correo: Optional[str] = Query(None),
    tipo: Optional[TipoColaborador] = Query(None),
    rol: Optional[str] = Query(None),
    estado: Optional[EstadoPersona] = Query(None),
    db: Session = Depends(get_db)
):
    service = PersonaService(db)
    items, total = service.list_colaboradores(page, limit, nombre, correo, tipo, rol, estado)
    meta = PaginationMeta(
        page=page, 
        limit=limit, 
        total=total, 
        total_pages=(total + limit - 1) // limit
    )
    return PaginatedResponse(
        data=PaginatedData(items=items, meta=meta),
        message="Lista de colaboradores obtenida correctamente"
    )

@router.get("/colaboradores/{id}", response_model=ResponseBase[ColaboradorResponseDTO])
def obtener_colaborador(
    id: int, 
    db: Session = Depends(get_db), 
    admin=Depends(get_current_admin)
):
    service = PersonaService(db)
    colaborador = service.get_colaborador_by_id(id)
    return ResponseBase(
        data=service._format_response(colaborador),
        message="Detalle del colaborador obtenido"
    )

@router.post("/colaboradores", response_model=ResponseBase[ColaboradorResponseDTO])
def crear_colaborador(
    nombres: str = Form(...),
    paterno: str = Form(...),
    materno: Optional[str] = Form(None),
    rol: str = Form(...),
    tipo: TipoColaborador = Form(...),
    correo: str = Form(...),
    presentacion: Optional[str] = Form(None),
    perfil: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    data = ColaboradorCreateDTO(
        nombres=nombres, 
        paterno=paterno, 
        materno=materno, 
        rol=rol, 
        tipo=tipo, 
        correo=correo, 
        presentacion=presentacion
    )
    service = PersonaService(db)
    colaborador = service.create_colaborador(data, perfil, admin)
    return ResponseBase(
        data=service._format_response(colaborador),
        message="Colaborador creado exitosamente"
    )

@router.put("/colaboradores/{id}", response_model=ResponseBase[ColaboradorResponseDTO])
def actualizar_colaborador(
    id: int,
    nombres: Optional[str] = Form(None),
    paterno: Optional[str] = Form(None),
    materno: Optional[str] = Form(None),
    rol: Optional[str] = Form(None),
    tipo: Optional[TipoColaborador] = Form(None),
    correo: Optional[str] = Form(None),
    presentacion: Optional[str] = Form(None),
    perfil: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    data = ColaboradorUpdateDTO(
        nombres=nombres,
        paterno=paterno,
        materno=materno,
        rol=rol,
        tipo=tipo,
        correo=correo,
        presentacion=presentacion
    )
    service = PersonaService(db)
    colaborador = service.update_colaborador(id, data, perfil, admin)
    return ResponseBase(
        data=service._format_response(colaborador),
        message="Colaborador actualizado correctamente"
    )

@router.patch("/colaboradores/{id}/baja", response_model=ResponseBase[dict])
def baja_colaborador(
    id: int, 
    db: Session = Depends(get_db), 
    admin=Depends(get_current_admin)
):
    service = PersonaService(db)
    service.delete_logic(id, admin)
    return ResponseBase(
        data={}, 
        message="Colaborador desactivado correctamente"
    )

@router.patch("/colaboradores/{id}/alta", response_model=ResponseBase[dict])
def alta_colaborador(
    id: int, 
    db: Session = Depends(get_db), 
    admin=Depends(get_current_admin)
):
    service = PersonaService(db)
    service.activate_logic(id, admin)
    return ResponseBase(
        data={}, 
        message="Colaborador activado correctamente"
    )

@router.delete("/colaboradores/{id}", response_model=ResponseBase[dict])
def eliminar_colaborador(
    id: int, 
    db: Session = Depends(get_db), 
    admin=Depends(get_current_admin)
):
    service = PersonaService(db)
    service.delete_physical(id, admin)
    return ResponseBase(
        data={}, 
        message="Colaborador y archivos eliminados permanentemente"
    )
