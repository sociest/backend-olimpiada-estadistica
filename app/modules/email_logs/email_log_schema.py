from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.modules.email_logs.email_log_model import EstadoEmail, TipoEmail

class ColegioMinimoLogDTO(BaseModel):
    nombre: str
    model_config = ConfigDict(from_attributes=True)

class EstudianteLogDTO(BaseModel):
    id_estudiante: int
    nombres: str
    paterno: str
    materno: Optional[str] = None
    colegio: Optional[ColegioMinimoLogDTO] = None
    
    model_config = ConfigDict(from_attributes=True)

class ContactoMinimoLogDTO(BaseModel):
    id_contacto: int
    nombre_completo: str
    
    model_config = ConfigDict(from_attributes=True)

class CampaniaMinimaLogDTO(BaseModel):
    id: int
    nombre: str
    
    model_config = ConfigDict(from_attributes=True)

class EmailLogResponseDTO(BaseModel):
    id: int
    destinatario: str
    asunto: str
    tipo: TipoEmail
    estado: EstadoEmail
    error: Optional[str]
    intentos: int
    ultimo_intento: Optional[datetime]
    fecha_creacion: datetime
    fecha_envio: Optional[datetime]
    id_estudiante: Optional[int]
    id_contacto: Optional[int]
    id_campania: Optional[int]

    model_config = ConfigDict(from_attributes=True)

class EmailLogCompletoResponseDTO(EmailLogResponseDTO):
    estudiante: Optional[EstudianteLogDTO] = None
    contacto: Optional[ContactoMinimoLogDTO] = None
    campania: Optional[CampaniaMinimaLogDTO] = None

    model_config = ConfigDict(from_attributes=True)