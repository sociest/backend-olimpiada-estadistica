from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.modules.personas.persona_schema import DirectorResponseDTO

class ColegioBaseDTO(BaseModel):
    codigo: int
    nombre: str
    tipo: str
    turno: str
    departamento: str
    municipio: str
    calle: Optional[str] = None
    estado: str


class ColegioCreateDTO(ColegioBaseDTO):
    pass


class ColegioUpdateDTO(BaseModel):
    codigo: Optional[int] = None
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    turno: Optional[str] = None
    departamento: Optional[str] = None
    municipio: Optional[str] = None
    calle: Optional[str] = None
    estado: Optional[str] = None


class ColegioResponseDTO(ColegioBaseDTO):
    id_colegio: int
    model_config = ConfigDict(from_attributes=True)

class ColegioDetailResponseDTO(ColegioResponseDTO):
    directores: List[DirectorResponseDTO] = []
    model_config = ConfigDict(from_attributes=True)


class DirectorCSVImportDTO(BaseModel):
    telefono_1: Optional[str] = None
    telefono_2: Optional[str] = None
    nombres: str
    paterno: str
    materno: Optional[str] = None


class ColegioCSVImportDTO(BaseModel):
    codigo: int
    nombre: str
    tipo: str
    turno: str
    departamento: str
    municipio: str
    calle: Optional[str] = None
    estado: str
    directores: List[DirectorCSVImportDTO]


class CSVImportErrorDTO(BaseModel):
    fila: int
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    error: str


class CSVImportResultDTO(BaseModel):
    validos: List[ColegioCSVImportDTO]
    errores: List[CSVImportErrorDTO]
    filas_error_csv: list[dict]
    
class CSVUploadResponseDTO(BaseModel):
    total_validos: int
    total_errores: int
    validos: List[ColegioCSVImportDTO]
    errores: List[CSVImportErrorDTO]
    filas_error_csv: list[dict]
    csv_errores_url: str | None = None

class CSVImportDBResponseDTO(BaseModel):
    insertados: int
    errores: List[CSVImportErrorDTO]