from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin
from app.core.responses import PaginatedData, PaginatedResponse, PaginationMeta, ResponseBase
from app.db.database import get_db
from app.modules.personas.persona_schema import (
    ColaboradorCreateDTO,
    ColaboradorResponseDTO,
    DirectorCreateDTO,
    DirectorResponseDTO,
    EstudianteCreateDTO,
    EstudianteResponseDTO,
    DirectorUpdateDTO,
    DirectorMinifiedDTO
)
from app.modules.personas.persona_service import PersonaService


router = APIRouter(prefix="/personas", tags=["personas"])


@router.get("/estudiantes", response_model=PaginatedResponse[EstudianteResponseDTO])
def listar_estudiantes(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    service = PersonaService(db)
    items, total = service.list_estudiantes(page=page, limit=limit)
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    data = PaginatedData(items=items, meta=meta)
    return PaginatedResponse(data=data, message="Lista obtenida correctamente")


@router.get("/directores", response_model=PaginatedResponse[DirectorResponseDTO])
def listar_directores(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    service = PersonaService(db)
    items, total = service.list_directores(page=page, limit=limit)
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    data = PaginatedData(items=items, meta=meta)
    return PaginatedResponse(data=data, message="Lista obtenida correctamente")


@router.get("/colaboradores", response_model=PaginatedResponse[ColaboradorResponseDTO])
def listar_colaboradores(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    service = PersonaService(db)
    items, total = service.list_colaboradores(page=page, limit=limit)
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    data = PaginatedData(items=items, meta=meta)
    return PaginatedResponse(data=data, message="Lista obtenida correctamente")


@router.post("/estudiantes", response_model=ResponseBase[EstudianteResponseDTO])
def crear_estudiante(
    data: EstudianteCreateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = PersonaService(db)
    estudiante = service.create_estudiante(data)
    return ResponseBase(data=estudiante, message="Operacion exitosa")


@router.post("/directores", response_model=ResponseBase[DirectorResponseDTO])
def crear_director(
    data: DirectorCreateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = PersonaService(db)
    director = service.create_director(data)
    return ResponseBase(data=director, message="Operacion exitosa")


@router.post("/colaboradores", response_model=ResponseBase[ColaboradorResponseDTO])
def crear_colaborador(
    data: ColaboradorCreateDTO,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = PersonaService(db)
    colaborador = service.create_colaborador(data)
    return ResponseBase(data=colaborador, message="Operacion exitosa")

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
    director = service.update_director(director_id, data)
    return ResponseBase(data=director, message="Director actualizado correctamente")

@router.patch("/directores/{director_id}/baja", response_model=ResponseBase[DirectorResponseDTO])
def baja_logica_director(director_id: int, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = PersonaService(db)
    director = service.delete_director_logic(director_id)
    return ResponseBase(data=director, message="Director dado de baja lógicamente")

@router.delete("/directores/{director_id}", response_model=ResponseBase[dict])
def eliminar_director_total(director_id: int, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = PersonaService(db)
    service.delete_director_total(director_id)
    return ResponseBase(data={}, message="Director eliminado permanentemente")