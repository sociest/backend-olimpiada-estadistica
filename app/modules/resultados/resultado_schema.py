from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.modules.resultados.resultado_model import EstadoResultado

class ResultadoBaseDTO(BaseModel):
    id_categoria: int
    id_fase_prueba: int
    id_inscripcion: int
    nota: int = Field(..., ge=0, le=100)
    observaciones: Optional[str] = None


class ResultadoCreateDTO(ResultadoBaseDTO):
    pass


class ResultadoUpdateDTO(BaseModel):
    nota: Optional[int] = Field(None, ge=0, le=100)
    observaciones: Optional[str] = None


class ResultadoEstadoUpdateDTO(BaseModel):
    estado: EstadoResultado


class ResultadoResponseDTO(ResultadoBaseDTO):
    id_resultado: int
    estado: EstadoResultado

    model_config = ConfigDict(from_attributes=True)


class ResultadoAprobatorioResponseDTO(BaseModel):
    id_inscripcion: int
    id_estudiante: int
    carnet_identidad: str
    nombres: str
    paterno: str
    materno: str
    nota: int


class ResultadoMasivoCreateDTO(BaseModel):
    id_categoria: int
    id_fase_prueba: int
    ids_inscripciones: List[int]


class ResultadoMasivoUpdateItemDTO(BaseModel):
    id_resultado: int
    nota: int = Field(..., ge=0, le=100)
    observaciones: Optional[str] = None


class ResultadoMasivoUpdateDTO(BaseModel):
    id_fase_prueba: int
    resultados: List[ResultadoMasivoUpdateItemDTO]