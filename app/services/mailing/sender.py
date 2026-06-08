import asyncio
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import case
from app.modules.email_logs.email_log_model import EmailLog, EstadoEmail, TipoEmail
from app.modules.campanias.campania_model import CampaniaEmail, EstadoCampania
from app.services.mailing.brevo_client import BrevoClient
from app.core.config import settings

class EmailSenderService:
    def __init__(self, db: Session):
        self.db = db
        self.brevo_client = BrevoClient()

    async def process_pending_emails(self):
        prioridad = case(
            (EmailLog.tipo == TipoEmail.RESPUESTA_CONTACTO, 1), 
            else_=2
        )

        pendientes = self.db.query(EmailLog).outerjoin(CampaniaEmail, EmailLog.id_campania == CampaniaEmail.id_campania_email)\
            .filter(
                EmailLog.estado == EstadoEmail.PENDIENTE,
                (CampaniaEmail.id_campania_email == None) | (CampaniaEmail.estado == EstadoCampania.EN_PROCESO)
            )\
            .order_by(prioridad.asc(), EmailLog.fecha_creacion.asc())\
            .limit(settings.mailing_batch_size).all()

        if not pendientes:
            return

        for log in pendientes:
            log.estado = EstadoEmail.EN_PROCESO
            log.ultimo_intento = datetime.now(timezone.utc)
            log.intentos += 1
        self.db.commit()

        for log in pendientes:
            try:
                if log.destinatario:
                    result = await self.brevo_client.send_email(
                        subject=log.asunto,
                        html_content=log.contenido_html,
                        to_email=log.destinatario
                    )
                    # Guardar el messageId de Brevo
                    log.brevo_message_id = result.get("messageId")
                log.estado = EstadoEmail.ENVIADO
                log.fecha_envio = datetime.now(timezone.utc)
            except Exception as e:
                log.error = str(e)
                if log.intentos >= settings.mailing_max_retries:
                    log.estado = EstadoEmail.FALLIDO
                else:
                    log.estado = EstadoEmail.PENDIENTE
        
        self.db.commit()