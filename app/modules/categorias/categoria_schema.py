from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.modules.categorias.categoria_model import EstadoEntidad, NivelEducativo


class CategoriaBaseDTO(BaseModel):
    id_convocatoria: int
    nombre_categoria: str
    curso: int = Field(..., ge=1, le=6)
    nivel: NivelEducativo


class CategoriaCreateDTO(CategoriaBaseDTO):
    pass


class CategoriaUpdateDTO(BaseModel):
    nombre_categoria: Optional[str] = None
    curso: Optional[int] = Field(None, ge=1, le=6)
    nivel: Optional[NivelEducativo] = None


class CategoriaEstadoUpdateDTO(BaseModel):
    estado: EstadoEntidad


class CategoriaResponseDTO(CategoriaBaseDTO):
    id_categoria: int
    estado: EstadoEntidad

    model_config = ConfigDict(from_attributes=True)

class CategoriaInicioDTO(BaseModel):
    nombre_categoria: str
    curso: str
    nivel: str

    model_config = ConfigDict(from_attributes=True)

class CategoriaDetalleDTO(CategoriaInicioDTO):
    id_categoria: int