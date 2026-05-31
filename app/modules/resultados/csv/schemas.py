from typing import List, Optional
from pydantic import BaseModel

class ValidRowDTO(BaseModel):
    ci: str
    nota: int
    id_inscripcion: int
    observaciones: Optional[str] = None

class ExistingRowDTO(BaseModel):
    ci: str
    resultado_csv: int
    resultado_actual: int
    id_inscripcion: int
    observaciones: Optional[str] = None

class ErrorRowDTO(BaseModel):
    fila: int
    ci: Optional[str] = None
    error: str

class AnalisisImportacionResponseDTO(BaseModel):
    token: str
    validos_nuevos: List[ValidRowDTO]
    existentes: List[ExistingRowDTO]
    errores: List[ErrorRowDTO]
    archivo_errores: Optional[str] = None

class ConfirmarImportacionDTO(BaseModel):
    token: str
    sobreescribir_existentes: bool