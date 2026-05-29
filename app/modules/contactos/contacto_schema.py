from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.modules.contactos.contacto_model import EstadoContacto
from app.modules.email_logs.email_log_schema import EmailLogResponseDTO

class ContactoCreateDTO(BaseModel):
    nombre_completo: str
    correo_electronico: str
    asunto: str
    mensaje: str

class ContactoRequestDTO(ContactoCreateDTO):
    username_hp: str = ""
    cf_turnstile_response: str = ""

class ContactoResponseDTO(BaseModel):
    id_contacto: int
    nombre_completo: str
    correo_electronico: str
    asunto: str
    mensaje: str
    estado: EstadoContacto
    creado_en: datetime
    cambio_en: datetime

    model_config = ConfigDict(from_attributes=True)

class ContactoCompletoResponseDTO(ContactoResponseDTO):
    email_logs: List[EmailLogResponseDTO] = []
    
    model_config = ConfigDict(from_attributes=True)

class BotonDTO(BaseModel):
    url: str
    texto: str

class ContactoRespuestaCreateDTO(BaseModel):
    asunto_correo: str
    contenido_mensaje: str
    contenido_secundario: Optional[str] = None
    boton: Optional[BotonDTO] = None