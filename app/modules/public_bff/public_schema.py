from datetime import date
from typing import List, Optional

from pydantic import BaseModel

from app.modules.convocatorias.convocatoria_schema import ConvocatoriaResponseDTO
from app.modules.materiales.material_schema import MaterialResponseDTO


class CategoriaInicioDTO(BaseModel):
    nombre_categoria: str
    nivel: str
    curso: int


class CategoriaDetalleDTO(BaseModel):
    nombre_categoria: str
    nivel: str
    curso: int


class MaterialPrincipalDTO(BaseModel):
    enlace_acceso: Optional[str] = None
    mensaje: Optional[str] = None


class MaterialPrincipalDetalleDTO(BaseModel):
    enlace_acceso: Optional[str] = None
    nombre_material: Optional[str] = None
    descripcion: Optional[str] = None


class MaterialPublicoSimpleDTO(BaseModel):
    enlace_acceso: str
    nombre_material: str
    descripcion: Optional[str] = None


class AvisoInicioDTO(BaseModel):
    titulo: str
    descripcion: str
    tipo: str
    fecha_publicacion: Optional[date] = None


class InicioResponseDTO(BaseModel):
    convocatoria: Optional[ConvocatoriaResponseDTO] = None
    material_principal: MaterialPrincipalDTO
    categorias: List[CategoriaInicioDTO]
    avisos: List[AvisoInicioDTO]


class ConvocatoriaDetalleDTO(BaseModel):
    convocatoria: Optional[ConvocatoriaResponseDTO] = None
    categorias: List[CategoriaDetalleDTO]
    materiales: List[MaterialPublicoSimpleDTO]
    afiche: Optional[MaterialPrincipalDetalleDTO] = None
    convocatoria_documento: Optional[MaterialPrincipalDetalleDTO] = None
    reglamento: Optional[MaterialPrincipalDetalleDTO] = None
