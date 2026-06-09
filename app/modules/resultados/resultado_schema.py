from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from app.modules.resultados.resultado_model import EstadoResultado

class ResultadoBaseDTO(BaseModel):
    id_categoria: int
    id_fase_prueba: int
    id_inscripcion: int
    nota: Decimal = Field(..., ge=0, le=100)
    observaciones: Optional[str] = None


class ResultadoCreateDTO(ResultadoBaseDTO):
    pass


class ResultadoUpdateDTO(BaseModel):
    nota: Optional[Decimal] = Field(None, ge=0, le=100)
    observaciones: Optional[str] = None


class ResultadoEstadoUpdateDTO(BaseModel):
    estado: EstadoResultado


class ResultadoResponseDTO(ResultadoBaseDTO):
    id_resultado: int
    estado: EstadoResultado
    carnet_identidad: str
    nombres: str
    paterno: str
    materno: Optional[str]
    model_config = ConfigDict(from_attributes=True)


class ResultadoAprobatorioResponseDTO(BaseModel):
    id_inscripcion: int
    id_estudiante: int
    carnet_identidad: str
    nombres: str
    paterno: str
    materno: Optional[str] = None
    nota: Decimal


class ResultadoMasivoCreateDTO(BaseModel):
    id_categoria: int
    id_fase_prueba: int
    ids_inscripciones: List[int]


class ResultadoMasivoUpdateItemDTO(BaseModel):
    id_resultado: int
    nota: Decimal = Field(..., ge=0, le=100)
    observaciones: Optional[str] = None


class ResultadoMasivoUpdateDTO(BaseModel):
    id_fase_prueba: int
    resultados: List[ResultadoMasivoUpdateItemDTO]

class ResultadoPublicoGeneralDTO(BaseModel):
    nombres: str
    paterno: str
    materno: Optional[str]
    carnet_identidad: str
    nota: Decimal

    model_config = ConfigDict(from_attributes=True)

class ResultadoPublicoFaseDTO(BaseModel):
    carnet_identidad: str
    nota: Decimal
    observaciones: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)