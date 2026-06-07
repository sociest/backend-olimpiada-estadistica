from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin
from app.core.responses import PaginatedData, PaginatedResponse, ResponseBase, PaginationMeta
from app.db.database import get_db
from app.modules.materiales.material_model import EstadoMaterial, TipoMaterialEnum
from app.modules.materiales.material_schema import (
    MaterialExternoCreateDTO,
    MaterialUpdateDTO,
    MaterialResponseDTO,
    MaterialDetalleResponseDTO,
    MaterialPrincipalResponse
)
from app.modules.materiales.material_service import MaterialService

router = APIRouter(prefix="/materiales", tags=["materiales"])


@router.get("", response_model=PaginatedResponse[MaterialResponseDTO])
def listar_materiales(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    estado: Optional[EstadoMaterial] = None,
    tipo_material: Optional[TipoMaterialEnum] = None,
    fc_start: Optional[datetime] = None,
    fc_end: Optional[datetime] = None,
    fa_start: Optional[datetime] = None,
    fa_end: Optional[datetime] = None,
    fp_start: Optional[datetime] = None,
    fp_end: Optional[datetime] = None,
    busqueda: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = MaterialService(db)
    skip = (page - 1) * limit
    items, total = service.get_all(skip, limit, estado, tipo_material, fc_start, fc_end, fa_start, fa_end, fp_start, fp_end, busqueda)
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    data = PaginatedData(items=items, meta=meta)
    return PaginatedResponse(data=data, message="Lista obtenida correctamente")


@router.get("/convocatoria/{id_convocatoria}", response_model=ResponseBase[List[MaterialResponseDTO]])
def obtener_por_convocatoria(id_convocatoria: int, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = MaterialService(db)
    items = service.get_by_convocatoria(id_convocatoria)
    return ResponseBase(data=items, message="Materiales de la convocatoria")


@router.get("/fase/{id_fase}", response_model=ResponseBase[List[MaterialResponseDTO]])
def obtener_por_fase(id_fase: int, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = MaterialService(db)
    items = service.get_by_fase(id_fase)
    return ResponseBase(data=items, message="Materiales de la fase")


@router.get("/convocatoria/{id_convocatoria}/principal/{tipo}", response_model=ResponseBase[MaterialResponseDTO])
def obtener_principal(id_convocatoria: int, tipo: TipoMaterialEnum, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = MaterialService(db)
    material = service.repository.get_material_principal(id_convocatoria, tipo)
    if not material: return ResponseBase(data=None, message="No se encontró", success=False)
    return ResponseBase(data=service._map_response(material), message="Material principal encontrado")


@router.get("/{id_material}", response_model=ResponseBase[MaterialDetalleResponseDTO])
def obtener_material(id_material: int, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = MaterialService(db)
    return ResponseBase(data=service.get_by_id(id_material), message="Operacion exitosa")


@router.post("/externo", response_model=ResponseBase[MaterialResponseDTO])
def crear_externo(data: MaterialExternoCreateDTO, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    service = MaterialService(db)
    return ResponseBase(data=service.create_externo(data, admin), message="Material externo creado")


@router.post("/archivo", response_model=ResponseBase[MaterialResponseDTO])
def crear_archivo(
    nombre_material: str = Form(...),
    descripcion: Optional[str] = Form(None),
    tipo_material: TipoMaterialEnum = Form(...),
    fecha_publicacion: Optional[datetime] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    service = MaterialService(db)
    resultado = service.create_archivo(nombre_material, descripcion, tipo_material, fecha_publicacion, file, admin)
    return ResponseBase(data=resultado, message="Material de archivo creado")


@router.post("/principal", response_model=ResponseBase[MaterialResponseDTO])
def crear_principal(
    id_convocatoria: int = Form(...),
    tipo_material: TipoMaterialEnum = Form(...),
    nombre_material: str = Form(...),
    descripcion: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    service = MaterialService(db)
    resultado = service.create_principal(id_convocatoria, tipo_material, nombre_material, descripcion, file, admin)
    return ResponseBase(data=resultado, message="Material principal creado y vinculado")


@router.put("/{id_material}", response_model=ResponseBase[MaterialResponseDTO])
def actualizar_material(id_material: int, data: MaterialUpdateDTO, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    service = MaterialService(db)
    return ResponseBase(data=service.update(id_material, data, admin), message="Material actualizado")


@router.put("/{id_material}/publicar", response_model=ResponseBase[MaterialResponseDTO])
def publicar_material(id_material: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    service = MaterialService(db)
    return ResponseBase(data=service.cambiar_estado(id_material, EstadoMaterial.PUBLICO, admin), message="Material publicado")


@router.put("/{id_material}/ocultar", response_model=ResponseBase[MaterialResponseDTO])
def ocultar_material(id_material: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    service = MaterialService(db)
    return ResponseBase(data=service.cambiar_estado(id_material, EstadoMaterial.OCULTO, admin), message="Material ocultado")


@router.post("/{id_material}/convocatoria/{id_convocatoria}", response_model=ResponseBase[dict])
def ligar_convocatoria(id_material: int, id_convocatoria: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    service = MaterialService(db)
    return ResponseBase(data=service.link_convocatoria(id_material, id_convocatoria, admin), message="Enlazado a convocatoria")


@router.delete("/{id_material}/convocatoria/{id_convocatoria}", response_model=ResponseBase[dict])
def desligar_convocatoria(id_material: int, id_convocatoria: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    service = MaterialService(db)
    return ResponseBase(data=service.unlink_convocatoria(id_material, id_convocatoria, admin), message="Desligado de convocatoria")


@router.post("/{id_material}/fase/{id_fase}", response_model=ResponseBase[dict])
def ligar_fase(id_material: int, id_fase: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    service = MaterialService(db)
    return ResponseBase(data=service.link_fase(id_material, id_fase, admin), message="Enlazado a fase")


@router.delete("/{id_material}/fase/{id_fase}", response_model=ResponseBase[dict])
def desligar_fase(id_material: int, id_fase: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    service = MaterialService(db)
    return ResponseBase(data=service.unlink_fase(id_material, id_fase, admin), message="Desligado de fase")


@router.delete("/{id_material}", response_model=ResponseBase[dict])
def eliminar_material(id_material: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    service = MaterialService(db)
    return ResponseBase(data=service.delete(id_material, admin), message="Material eliminado")

@router.get("/principal/{tipo_material}", response_model=ResponseBase[List[MaterialPrincipalResponse]])
def obtener_materiales_principales(tipo_material: TipoMaterialEnum, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    service = MaterialService(db)
    return ResponseBase(data=service.get_material_principal_by_tipo(tipo_material), message="Materiales principales obtenidos")

@router.get("/principal/convocatoria/{id_convocatoria}", response_model=ResponseBase[MaterialPrincipalResponse])
def obtener_material_principal_por_convocatoria(id_convocatoria: int, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    service = MaterialService(db)
    return ResponseBase(data=service.get_material_principal_by_convocatoria(id_convocatoria), message="Material principal obtenido")

@router.put("/principal/convocatoria/{id_convocatoria}/tipo/{tipo_material}", response_model=ResponseBase[dict])
def ligar_material_principal_convocatoria(id_convocatoria: int, tipo_material: TipoMaterialEnum, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    service = MaterialService(db)
    return ResponseBase(data=service.link_material_principal_tipo(id_convocatoria, tipo_material, admin), message="Material principal enlazado a convocatoria")