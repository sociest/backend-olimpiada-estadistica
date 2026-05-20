from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin
from app.core.responses import PaginatedData, PaginatedResponse, PaginationMeta, ResponseBase
from app.db.database import get_db
from app.modules.materiales.material_schema import MaterialCreateDTO, MaterialResponseDTO, MaterialUpdateDTO
from app.modules.materiales.material_service import MaterialService


router = APIRouter(prefix="/materiales", tags=["materiales"])


@router.get("", response_model=PaginatedResponse[MaterialResponseDTO])
def listar_materiales(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    service = MaterialService(db)
    items, total = service.get_public(page=page, limit=limit)
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    data = PaginatedData(items=items, meta=meta)
    return PaginatedResponse(data=data, message="Lista obtenida correctamente")


@router.get("/admin", response_model=PaginatedResponse[MaterialResponseDTO])
def listar_materiales_admin(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = MaterialService(db)
    items, total = service.get_all(page=page, limit=limit)
    meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=(total + limit - 1) // limit)
    data = PaginatedData(items=items, meta=meta)
    return PaginatedResponse(data=data, message="Lista obtenida correctamente")


@router.get("/principales", response_model=ResponseBase[list[MaterialResponseDTO]])
def listar_materiales_principales(
    importancia_tipo: str | None = None,
    db: Session = Depends(get_db),
):
    service = MaterialService(db)
    materiales = service.get_principales_public(importancia_tipo)
    return ResponseBase(data=materiales, message="Operacion exitosa")


@router.get("/{material_id}", response_model=ResponseBase[MaterialResponseDTO])
def obtener_material(material_id: int, db: Session = Depends(get_db)):
    service = MaterialService(db)
    material = service.get_public_by_id(material_id)
    return ResponseBase(data=material, message="Operacion exitosa")


@router.post("", response_model=ResponseBase[MaterialResponseDTO])
async def crear_material(
    nombre_material: str = Form(...),
    tipo_material: str = Form(...),
    descripcion: Optional[str] = Form(None),
    fecha_publicacion: Optional[datetime] = Form(None),
    id_convocatoria: Optional[int] = Form(None),
    id_categoria: Optional[int] = Form(None),
    id_fase: Optional[int] = Form(None),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    data = MaterialCreateDTO(
        nombre_material=nombre_material,
        descripcion=descripcion,
        tipo_material=tipo_material,
        fecha_publicacion=fecha_publicacion,
        id_convocatoria=id_convocatoria,
        id_categoria=id_categoria,
        id_fase=id_fase,
    )
    service = MaterialService(db)
    material = await service.create(data, archivo, current_admin_id)
    return ResponseBase(data=material, message="Operacion exitosa")


@router.post("/convocatorias/{convocatoria_id}", response_model=ResponseBase[MaterialResponseDTO])
async def crear_material_convocatoria(
    convocatoria_id: int,
    nombre_material: str = Form(...),
    tipo_material: str = Form(...),
    descripcion: Optional[str] = Form(None),
    fecha_publicacion: Optional[datetime] = Form(None),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    data = MaterialCreateDTO(
        nombre_material=nombre_material,
        descripcion=descripcion,
        tipo_material=tipo_material,
        fecha_publicacion=fecha_publicacion,
    )
    service = MaterialService(db)
    material = await service.create_material_convocatoria(convocatoria_id, data, archivo, current_admin_id)
    return ResponseBase(data=material, message="Operacion exitosa")


@router.post("/categorias/{categoria_id}", response_model=ResponseBase[MaterialResponseDTO])
async def crear_material_categoria(
    categoria_id: int,
    nombre_material: str = Form(...),
    tipo_material: str = Form(...),
    descripcion: Optional[str] = Form(None),
    fecha_publicacion: Optional[datetime] = Form(None),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    data = MaterialCreateDTO(
        nombre_material=nombre_material,
        descripcion=descripcion,
        tipo_material=tipo_material,
        fecha_publicacion=fecha_publicacion,
    )
    service = MaterialService(db)
    material = await service.create_material_categoria(categoria_id, data, archivo, current_admin_id)
    return ResponseBase(data=material, message="Operacion exitosa")


@router.post("/fases/{fase_id}", response_model=ResponseBase[MaterialResponseDTO])
async def crear_material_fase(
    fase_id: int,
    nombre_material: str = Form(...),
    tipo_material: str = Form(...),
    descripcion: Optional[str] = Form(None),
    fecha_publicacion: Optional[datetime] = Form(None),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    data = MaterialCreateDTO(
        nombre_material=nombre_material,
        descripcion=descripcion,
        tipo_material=tipo_material,
        fecha_publicacion=fecha_publicacion,
    )
    service = MaterialService(db)
    material = await service.create_material_fase(fase_id, data, archivo, current_admin_id)
    return ResponseBase(data=material, message="Operacion exitosa")


@router.get("/convocatorias/{convocatoria_id}/afiche", response_model=ResponseBase[MaterialResponseDTO])
def obtener_afiche(convocatoria_id: int, db: Session = Depends(get_db)):
    service = MaterialService(db)
    material = service.get_material_principal_public(convocatoria_id, "AFICHE")
    return ResponseBase(data=material, message="Operacion exitosa")


@router.get("/convocatorias/{convocatoria_id}/convocatoria", response_model=ResponseBase[MaterialResponseDTO])
def obtener_convocatoria(convocatoria_id: int, db: Session = Depends(get_db)):
    service = MaterialService(db)
    material = service.get_material_principal_public(convocatoria_id, "CONVOCATORIA")
    return ResponseBase(data=material, message="Operacion exitosa")


@router.get("/convocatorias/{convocatoria_id}/reglamento", response_model=ResponseBase[MaterialResponseDTO])
def obtener_reglamento(convocatoria_id: int, db: Session = Depends(get_db)):
    service = MaterialService(db)
    material = service.get_material_principal_public(convocatoria_id, "REGLAMENTO")
    return ResponseBase(data=material, message="Operacion exitosa")




@router.post("/convocatorias/{convocatoria_id}/afiche", response_model=ResponseBase[MaterialResponseDTO])
async def crear_afiche(
    convocatoria_id: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    data = MaterialCreateDTO(
        nombre_material="",
        descripcion=None,
        tipo_material="AFICHE",
        fecha_publicacion=None,
    )
    service = MaterialService(db)
    material = await service.create_material_principal(
        convocatoria_id,
        "AFICHE",
        data,
        archivo,
        current_admin_id,
    )
    return ResponseBase(data=material, message="Operacion exitosa")


@router.post("/convocatorias/{convocatoria_id}/convocatoria", response_model=ResponseBase[MaterialResponseDTO])
async def crear_convocatoria_principal(
    convocatoria_id: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    data = MaterialCreateDTO(
        nombre_material="",
        descripcion=None,
        tipo_material="CONVOCATORIA",
        fecha_publicacion=None,
    )
    service = MaterialService(db)
    material = await service.create_material_principal(
        convocatoria_id,
        "CONVOCATORIA",
        data,
        archivo,
        current_admin_id,
    )
    return ResponseBase(data=material, message="Operacion exitosa")


@router.post("/convocatorias/{convocatoria_id}/reglamento", response_model=ResponseBase[MaterialResponseDTO])
async def crear_reglamento(
    convocatoria_id: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    data = MaterialCreateDTO(
        nombre_material="",
        descripcion=None,
        tipo_material="REGLAMENTO",
        fecha_publicacion=None,
    )
    service = MaterialService(db)
    material = await service.create_material_principal(
        convocatoria_id,
        "REGLAMENTO",
        data,
        archivo,
        current_admin_id,
    )
    return ResponseBase(data=material, message="Operacion exitosa")


@router.put("/convocatorias/{convocatoria_id}/afiche", response_model=ResponseBase[MaterialResponseDTO])
async def actualizar_afiche(
    convocatoria_id: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    data = MaterialCreateDTO(
        nombre_material="",
        descripcion=None,
        tipo_material="AFICHE",
        fecha_publicacion=None,
    )
    service = MaterialService(db)
    material = await service.create_material_principal(
        convocatoria_id,
        "AFICHE",
        data,
        archivo,
        current_admin_id,
    )
    return ResponseBase(data=material, message="Operacion exitosa")


@router.put("/convocatorias/{convocatoria_id}/convocatoria", response_model=ResponseBase[MaterialResponseDTO])
async def actualizar_convocatoria_principal(
    convocatoria_id: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    data = MaterialCreateDTO(
        nombre_material="",
        descripcion=None,
        tipo_material="CONVOCATORIA",
        fecha_publicacion=None,
    )
    service = MaterialService(db)
    material = await service.create_material_principal(
        convocatoria_id,
        "CONVOCATORIA",
        data,
        archivo,
        current_admin_id,
    )
    return ResponseBase(data=material, message="Operacion exitosa")


@router.put("/convocatorias/{convocatoria_id}/reglamento", response_model=ResponseBase[MaterialResponseDTO])
async def actualizar_reglamento(
    convocatoria_id: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    data = MaterialCreateDTO(
        nombre_material="",
        descripcion=None,
        tipo_material="REGLAMENTO",
        fecha_publicacion=None,
    )
    service = MaterialService(db)
    material = await service.create_material_principal(
        convocatoria_id,
        "REGLAMENTO",
        data,
        archivo,
        current_admin_id,
    )
    return ResponseBase(data=material, message="Operacion exitosa")


@router.delete("/convocatorias/{convocatoria_id}/afiche", response_model=ResponseBase[MaterialResponseDTO])
def eliminar_afiche(
    convocatoria_id: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = MaterialService(db)
    material = service.delete_material_principal(convocatoria_id, "AFICHE", current_admin_id)
    return ResponseBase(data=material, message="Operacion exitosa")


@router.delete("/convocatorias/{convocatoria_id}/convocatoria", response_model=ResponseBase[MaterialResponseDTO])
def eliminar_convocatoria_principal(
    convocatoria_id: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = MaterialService(db)
    material = service.delete_material_principal(convocatoria_id, "CONVOCATORIA", current_admin_id)
    return ResponseBase(data=material, message="Operacion exitosa")


@router.delete("/convocatorias/{convocatoria_id}/reglamento", response_model=ResponseBase[MaterialResponseDTO])
def eliminar_reglamento(
    convocatoria_id: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = MaterialService(db)
    material = service.delete_material_principal(convocatoria_id, "REGLAMENTO", current_admin_id)
    return ResponseBase(data=material, message="Operacion exitosa")


@router.post("/convocatorias/{convocatoria_id}/afiche/asignar", response_model=ResponseBase[MaterialResponseDTO])
def asignar_afiche(
    convocatoria_id: int,
    material_id: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = MaterialService(db)
    material = service.asignar_material_principal(convocatoria_id, material_id, "AFICHE", current_admin_id)
    return ResponseBase(data=material, message="Operacion exitosa")


@router.post("/convocatorias/{convocatoria_id}/convocatoria/asignar", response_model=ResponseBase[MaterialResponseDTO])
def asignar_convocatoria_principal(
    convocatoria_id: int,
    material_id: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = MaterialService(db)
    material = service.asignar_material_principal(convocatoria_id, material_id, "CONVOCATORIA", current_admin_id)
    return ResponseBase(data=material, message="Operacion exitosa")


@router.post("/convocatorias/{convocatoria_id}/reglamento/asignar", response_model=ResponseBase[MaterialResponseDTO])
def asignar_reglamento(
    convocatoria_id: int,
    material_id: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = MaterialService(db)
    material = service.asignar_material_principal(convocatoria_id, material_id, "REGLAMENTO", current_admin_id)
    return ResponseBase(data=material, message="Operacion exitosa")


@router.put("/{material_id}", response_model=ResponseBase[MaterialResponseDTO])
async def actualizar_material(
    material_id: int,
    nombre_material: Optional[str] = Form(None),
    tipo_material: Optional[str] = Form(None),
    descripcion: Optional[str] = Form(None),
    fecha_publicacion: Optional[datetime] = Form(None),
    id_convocatoria: Optional[int] = Form(None),
    id_categoria: Optional[int] = Form(None),
    id_fase: Optional[int] = Form(None),
    archivo: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    data = MaterialUpdateDTO(
        nombre_material=nombre_material,
        descripcion=descripcion,
        tipo_material=tipo_material,
        fecha_publicacion=fecha_publicacion,
        id_convocatoria=id_convocatoria,
        id_categoria=id_categoria,
        id_fase=id_fase,
    )
    service = MaterialService(db)
    material = await service.update(material_id, data, archivo, current_admin_id)
    return ResponseBase(data=material, message="Operacion exitosa")


@router.delete("/{material_id}", response_model=ResponseBase[MaterialResponseDTO])
def eliminar_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin),
):
    service = MaterialService(db)
    material = service.delete(material_id, current_admin_id)
    return ResponseBase(data=material, message="Operacion exitosa")
