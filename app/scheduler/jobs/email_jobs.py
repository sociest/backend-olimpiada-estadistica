import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.modules.campanias.campania_model import CampaniaEmail, EstadoCampania, CampaniaDestinatario
from app.modules.email_logs.email_log_model import EmailLog, EstadoEmail, TipoEmail
from app.services.mailing.brevo_client import BrevoClient
from app.services.mailing.renderer import EmailRenderer
from app.core.config import settings

brevo_client = BrevoClient()
renderer = EmailRenderer()

def process_scheduled_campaigns():
    """Busca campañas PROGRAMADAS y las pasa a EN_PROCESO, generando sus EmailLogs."""
    db: Session = SessionLocal()
    try:
        campanias = db.query(CampaniaEmail).filter(
            CampaniaEmail.estado == EstadoCampania.PROGRAMADA,
            CampaniaEmail.fecha_programada <= datetime.now()
        ).all()

        for camp in campanias:
            camp.estado = EstadoCampania.EN_PROCESO
            camp.fecha_inicio = datetime.now()
            
            destinatarios = db.query(CampaniaDestinatario).filter_by(id_campania=camp.id).all()
            
            for dest in destinatarios:
                html_content = renderer.render_campania(
                    title=camp.nombre,
                    asunto=camp.asunto,
                    usuario=dest.estudiante.nombres, # Usando properties del modelo Estudiante
                    contenido_mensaje="Este es un mensaje automático de campaña."
                )
                
                log = EmailLog(
                    destinatario=dest.estudiante.correo,
                    asunto=camp.asunto,
                    contenido_html=html_content,
                    tipo=TipoEmail.MASIVO_INSCRIPCION,
                    estado=EstadoEmail.PENDIENTE,
                    id_estudiante=dest.id_estudiante,
                    id_campania=camp.id
                )
                db.add(log)
            
            db.commit()
    finally:
        db.close()

async def send_pending_emails():
    """Procesa un lote de emails PENDIENTES."""
    db: Session = SessionLocal()
    try:
        # Solo emails de campañas que NO estén canceladas/fallidas
        pendientes = db.query(EmailLog).join(CampaniaEmail, EmailLog.id_campania == CampaniaEmail.id)\
            .filter(
                EmailLog.estado == EstadoEmail.PENDIENTE,
                CampaniaEmail.estado == EstadoCampania.EN_PROCESO
            )\
            .limit(settings.mailing_batch_size).all()

        if not pendientes:
            return

        for log in pendientes:
            log.estado = EstadoEmail.EN_PROCESO
            log.ultimo_intento = datetime.now()
            log.intentos += 1
        db.commit()

        for log in pendientes:
            try:
                if log.destinatario:
                    await brevo_client.send_email(
                        subject=log.asunto,
                        html_content=log.contenido_html,
                        to_email=log.destinatario
                    )
                log.estado = EstadoEmail.ENVIADO
                log.fecha_envio = datetime.now()
            except Exception as e:
                log.error = str(e)
                if log.intentos >= settings.mailing_max_retries:
                    log.estado = EstadoEmail.FALLIDO
                else:
                    log.estado = EstadoEmail.PENDIENTE
        
        db.commit()
    finally:
        db.close()

def finalize_campaigns():
    """Cierra campañas que ya no tienen emails pendientes o en proceso."""
    db: Session = SessionLocal()
    try:
        en_proceso = db.query(CampaniaEmail).filter(CampaniaEmail.estado == EstadoCampania.EN_PROCESO).all()
        
        for camp in en_proceso:
            pendientes = db.query(EmailLog).filter(
                EmailLog.id_campania == camp.id,
                EmailLog.estado.in_([EstadoEmail.PENDIENTE, EstadoEmail.EN_PROCESO])
            ).count()
            
            if pendientes == 0:
                camp.estado = EstadoCampania.FINALIZADA
                camp.fecha_fin = datetime.now()
        
        db.commit()
    finally:
        db.close()