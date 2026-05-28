from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.modules.campanias.campania_model import EstadoCampania

class EnlaceDTO(BaseModel):
    url: str
    texto_url: str

class CampaniaCreateDTO(BaseModel):
    nombre: str
    asunto: str
    fecha_programada: Optional[datetime] = None
    destinatarios_ids: Optional[List[int]] = []

class CampaniaUpdateDTO(BaseModel):
    nombre: Optional[str] = None
    asunto: Optional[str] = None
    fecha_programada: Optional[datetime] = None
    agregar_destinatarios: Optional[List[int]] = []
    eliminar_destinatarios: Optional[List[int]] = []

class CampaniaResponseDTO(BaseModel):
    id: int
    nombre: str
    asunto: str
    estado: EstadoCampania
    fecha_creacion: datetime
    fecha_programada: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)