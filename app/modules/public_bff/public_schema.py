from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel

from app.modules.avisos.aviso_model import AvisoPrioridad, TipoAviso
from app.modules.categorias.categoria_model import EstadoEntidad, NivelEducativo
from app.modules.colegios.colegio_model import TurnoColegio
from app.modules.convocatorias.convocatoria_schema import ConvocatoriaResponseDTO
from app.modules.fases.fase_model import ModalidadFase
from app.modules.materiales.material_model import TipoMaterialEnum

class CategoriaInicioDTO(BaseModel):
    id_categoria: int
    nombre_categoria: str
    nivel: NivelEducativo
    curso: int

class CategoriaDetalleDTO(BaseModel):
    id_categoria: int
    nombre_categoria: str
    nivel: NivelEducativo
    curso: int

class MaterialPrincipalDTO(BaseModel):
    enlace_acceso: Optional[str] = None
    importancia_tipo: Optional[TipoMaterialEnum] = None

class MaterialPrincipalDetalleDTO(BaseModel):
    enlace_acceso: Optional[str] = None
    nombre_material: Optional[str] = None
    descripcion: Optional[str] = None

class MaterialPublicoSimpleDTO(BaseModel):
    enlace_acceso: str
    nombre_material: str
    descripcion: Optional[str] = None

class FasePreparacionPublicaDTO(BaseModel):
    id_fase: int
    id_categoria_fk: int
    nombre_fase: str
    descripcion: Optional[str] = None
    modalidad: ModalidadFase
    estado: EstadoEntidad
    tipo_fase: str = "PREPARACION"
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None

class FasePruebaPublicaDTO(BaseModel):
    id_fase: int
    id_categoria_fk: int
    nombre_fase: str
    descripcion: Optional[str] = None
    modalidad: ModalidadFase
    estado: EstadoEntidad
    tipo_fase: str = "PRUEBA"
    id_fase_anterior: Optional[int] = None
    criterio_aprobacion: Optional[int] = None
    fecha_realizacion: Optional[datetime] = None
    lugar_realizacion: Optional[str] = None

class AvisoInicioDTO(BaseModel):
    titulo: str
    descripcion: str
    tipo: TipoAviso
    prioridad: AvisoPrioridad
    fecha_publicacion: Optional[date] = None
    estado_temporal: Optional[str] = None

class InicioResponseDTO(BaseModel):
    convocatoria: Optional[ConvocatoriaResponseDTO] = None
    material_principal: List[MaterialPrincipalDTO]
    categorias: List[CategoriaInicioDTO]
    avisos: List[AvisoInicioDTO]

class ConvocatoriaDetalleDTO(BaseModel):
    convocatoria: Optional[ConvocatoriaResponseDTO] = None
    categorias: List[CategoriaDetalleDTO]
    materiales: List[MaterialPublicoSimpleDTO]
    afiche: Optional[MaterialPrincipalDetalleDTO] = None
    convocatoria_documento: Optional[MaterialPrincipalDetalleDTO] = None
    reglamento: Optional[MaterialPrincipalDetalleDTO] = None

class ColegioPublicoSimpleDTO(BaseModel):
    id_colegio: int
    nombre: str
    municipio: str
    turno: TurnoColegio
