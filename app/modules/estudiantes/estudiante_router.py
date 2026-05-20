from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.responses import ResponseBase
from app.db.database import get_db
from app.modules.estudiantes.estudiante_schema import EstudianteEncontradoDTO, EstudianteUpdateDTO
from app.modules.estudiantes.estudiante_service import EstudianteService


router = APIRouter(prefix="/estudiantes", tags=["estudiantes"])


@router.get("/buscar", response_model=ResponseBase[EstudianteEncontradoDTO])
def buscar_estudiante(
    carnet_identidad: str,
    fecha_nacimiento: date,
    db: Session = Depends(get_db),
):
    service = EstudianteService(db)
    estudiante = service.buscar_por_documento_fecha(carnet_identidad, fecha_nacimiento)
    return ResponseBase(data=estudiante, message="Operacion exitosa")


@router.patch("/{estudiante_id}", response_model=ResponseBase[EstudianteEncontradoDTO])
def actualizar_estudiante(
    estudiante_id: int,
    data: EstudianteUpdateDTO,
    db: Session = Depends(get_db),
):
    service = EstudianteService(db)
    estudiante = service.update(estudiante_id, data)
    return ResponseBase(data=estudiante, message="Operacion exitosa")
