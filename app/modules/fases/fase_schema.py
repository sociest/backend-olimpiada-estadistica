from datetime import datetime
from typing import Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from app.modules.fases.fase_model import EstadoEntidad, ModalidadFase


class FaseBaseDTO(BaseModel):
    id_categoria_fk: int
    nombre_fase: str
    descripcion: Optional[str] = None
    modalidad: ModalidadFase


class FaseEstadoUpdateDTO(BaseModel):
    estado: EstadoEntidad


class FasePreparacionCreateDTO(FaseBaseDTO):
    fecha_inicio: datetime
    fecha_fin: datetime


class FasePreparacionUpdateDTO(BaseModel):
    nombre_fase: Optional[str] = None
    descripcion: Optional[str] = None
    modalidad: Optional[ModalidadFase] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None


class FasePreparacionResponseDTO(FasePreparacionCreateDTO):
    id_fase: int
    estado: EstadoEntidad
    tipo_fase: Literal["PREPARACION"] = "PREPARACION"

    model_config = ConfigDict(from_attributes=True)


class FasePruebaCreateDTO(FaseBaseDTO):
    id_fase_anterior: Optional[int] = None
    criterio_aprobacion: int = Field(..., ge=0)
    fecha_realizacion: datetime
    lugar_realizacion: Optional[str] = None


class FasePruebaUpdateDTO(BaseModel):
    nombre_fase: Optional[str] = None
    descripcion: Optional[str] = None
    modalidad: Optional[ModalidadFase] = None
    id_fase_anterior: Optional[int] = None
    criterio_aprobacion: Optional[int] = Field(None, ge=0)
    fecha_realizacion: Optional[datetime] = None
    lugar_realizacion: Optional[str] = None


class FasePruebaResponseDTO(FasePruebaCreateDTO):
    id_fase: int
    estado: EstadoEntidad
    tipo_fase: Literal["PRUEBA"] = "PRUEBA"

    model_config = ConfigDict(from_attributes=True)


FaseResponsePolymorphic = Union[FasePruebaResponseDTO, FasePreparacionResponseDTO]