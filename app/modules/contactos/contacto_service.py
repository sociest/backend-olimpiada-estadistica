from sqlalchemy.orm import Session
from app.core.exceptions import NotFoundError, BusinessRuleError
from app.modules.auth.auth_repository import AuthRepository
from app.modules.contactos.contacto_model import ContactoModel, EstadoContacto
from app.modules.contactos.contacto_repository import ContactoRepository
from app.modules.contactos.contacto_schema import ContactoCreateDTO, ContactoRespuestaCreateDTO
from app.modules.email_logs.email_log_model import EmailLog, EstadoEmail, TipoEmail
from app.services.mailing.renderer import EmailRenderer

class ContactoService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = ContactoRepository(db)
        self.auth_repository = AuthRepository(db)
        self.renderer = EmailRenderer()

    def get_by_id(self, contacto_id: int):
        contacto = self.repository.get_by_id(contacto_id)
        if not contacto:
            raise NotFoundError("Mensaje de contacto no encontrado")
        return contacto

    def get_all(self, page: int, limit: int, **filters):
        skip = (page - 1) * limit
        return self.repository.get_all(skip=skip, limit=limit, **filters)

    def get_all_respondidos(self, page: int, limit: int, **filters):
        skip = (page - 1) * limit
        return self.repository.get_all_respondidos(skip=skip, limit=limit, **filters)

    def create(self, data: ContactoCreateDTO):
        contacto = ContactoModel(
            nombre_completo=data.nombre_completo,
            correo_electronico=data.correo_electronico,
            asunto=data.asunto,
            mensaje=data.mensaje,
            estado=EstadoContacto.PENDIENTE
        )
        return self.repository.create(contacto)

    def marcar_leido(self, contacto_id: int, current_admin_id: int):
        contacto = self.get_by_id(contacto_id)
        if contacto.estado != EstadoContacto.PENDIENTE:
            raise BusinessRuleError("Solo se pueden marcar como leídos los contactos PENDIENTES")
            
        contacto.estado = EstadoContacto.LEIDO
        self.repository.update()
        self.db.refresh(contacto)
        self.auth_repository.create_auditoria(admin_id=current_admin_id, accion="LEER_CONTACTO", descripcion=f"Contacto {contacto.id_contacto} marcado como leído")
        return contacto

    def responder(self, contacto_id: int, data: ContactoRespuestaCreateDTO, current_admin_id: int):
        contacto = self.get_by_id(contacto_id)
        if contacto.estado == EstadoContacto.RESPONDIDO:
            raise BusinessRuleError("Este contacto ya ha sido respondido")

        dict_enlaces = [e.model_dump() for e in data.enlaces] if data.enlaces else []

        html_content = self.renderer.render_respuesta_contacto(
            asunto_correo=data.asunto_correo,
            usuario=contacto.nombre_completo,
            asunto_original=contacto.asunto,
            contenido_mensaje=data.contenido_mensaje,
            contenido_secundario=data.contenido_secundario,
            enlaces=dict_enlaces
        )

        email_log = EmailLog(
            destinatario=contacto.correo_electronico,
            asunto=data.asunto_correo,
            contenido_html=html_content,
            tipo=TipoEmail.RESPUESTA_CONTACTO,
            estado=EstadoEmail.PENDIENTE,
            id_contacto=contacto.id_contacto
        )
        self.db.add(email_log)
        
        contacto.estado = EstadoContacto.RESPONDIDO
        self.repository.update()
        self.db.refresh(contacto)
        
        self.auth_repository.create_auditoria(
            admin_id=current_admin_id, 
            accion="RESPONDER_CONTACTO", 
            descripcion=f"Respuesta generada para contacto {contacto.id_contacto}"
        )
        return contacto

    def delete(self, contacto_id: int, current_admin_id: int):
        contacto = self.get_by_id(contacto_id)
        self.repository.delete(contacto)
        self.auth_repository.create_auditoria(admin_id=current_admin_id, accion="ELIMINAR_CONTACTO", descripcion=f"Mensaje de contacto eliminado: {contacto.correo_electronico}")
        return None