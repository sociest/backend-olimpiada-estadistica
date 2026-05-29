import asyncio
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.modules.campanias.campania_model import CampaniaEmail, EstadoCampania, CampaniaDestinatario
from app.modules.email_logs.email_log_model import EmailLog, EstadoEmail, TipoEmail
from app.services.mailing.renderer import EmailRenderer
from app.services.mailing.sender import EmailSenderService
from app.core.config import settings

logger = logging.getLogger(__name__)

def get_local_now():
    tz = ZoneInfo(settings.scheduler_timezone)
    return datetime.now(tz).replace(tzinfo=None)

def process_scheduled_campaigns():
    logger.debug("Ejecutando Job: Búsqueda de campañas programadas...")
    db: Session = SessionLocal()
    renderer = EmailRenderer()
    
    try:
        ahora = get_local_now()
        campanias = db.query(CampaniaEmail).filter(
            CampaniaEmail.estado == EstadoCampania.PROGRAMADA,
            CampaniaEmail.fecha_programada <= ahora
        ).all()

        if campanias:
            logger.info(f"¡Se encontraron {len(campanias)} campañas listas para procesar!")

        for camp in campanias:
            logger.info(f"Procesando campaña ID: {camp.id} - {camp.nombre}")
            camp.estado = EstadoCampania.EN_PROCESO
            camp.fecha_inicio = ahora
            
            destinatarios = db.query(CampaniaDestinatario).filter_by(id_campania=camp.id).all()
            
            for dest in destinatarios:
                estudiante = dest.estudiante
                if not estudiante or not estudiante.correo:
                    logger.warning(f"Se omitió al estudiante ID {dest.id_estudiante} por falta de correo.")
                    continue

                html_content = renderer.render_campania(
                    asunto=camp.asunto,
                    usuario=estudiante.nombres,
                    contenido_mensaje=camp.contenido_mensaje,
                    contenido_secundario=camp.contenido_secundario,
                    enlaces=camp.enlaces
                )
                
                log = EmailLog(
                    destinatario=estudiante.correo,
                    asunto=camp.asunto,
                    contenido_html=html_content,
                    tipo=TipoEmail.MASIVO_INSCRIPCION,
                    estado=EstadoEmail.PENDIENTE,
                    id_estudiante=dest.id_estudiante,
                    id_campania=camp.id
                )
                db.add(log)
            
            db.commit()
            logger.info(f"Campaña {camp.id} pasada a EN_PROCESO. Logs generados.")
            
    except Exception as e:
        db.rollback()
        logger.error(f"Error procesando campañas: {str(e)}", exc_info=True)
    finally:
        db.close()

async def send_pending_emails():
    logger.debug("Ejecutando Job: Envío de correos pendientes...")
    db: Session = SessionLocal()
    try:
        sender_service = EmailSenderService(db)
        await sender_service.process_pending_emails()
    except Exception as e:
        logger.error(f"Error en el envío de correos: {str(e)}", exc_info=True)
    finally:
        db.close()

def finalize_campaigns():
    logger.debug("Ejecutando Job: Verificación de campañas finalizadas...")
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
                camp.fecha_fin = get_local_now()
                logger.info(f"Campaña ID {camp.id} ha sido FINALIZADA exitosamente.")
        
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error finalizando campañas: {str(e)}", exc_info=True)
    finally:
        db.close()