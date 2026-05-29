import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

from app.scheduler.jobs.email_jobs import process_scheduled_campaigns, send_pending_emails, finalize_campaigns
from app.core.config import settings

logger = logging.getLogger(__name__)

jobstores = {
    'default': MemoryJobStore()
}
scheduler = AsyncIOScheduler(jobstores=jobstores, timezone=settings.scheduler_timezone)
def listener_errores_scheduler(event):
    if event.exception:
        logger.error(f"El Job {event.job_id} falló de forma crítica: {event.exception}")
    else:
        logger.debug(f"Job {event.job_id} ejecutado correctamente.")

def start_scheduler():
    if settings.scheduler_enabled:
        logger.info("Iniciando APScheduler...")

        scheduler.add_listener(listener_errores_scheduler, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

        scheduler.add_job(process_scheduled_campaigns, 'interval', minutes=1, id='process_campaigns', replace_existing=True)
        scheduler.add_job(send_pending_emails, 'interval', minutes=settings.mailing_interval_minutes, id='send_emails', replace_existing=True)
        scheduler.add_job(finalize_campaigns, 'interval', minutes=2, id='finalize_campaigns', replace_existing=True)
        
        scheduler.start()
        logger.info("APScheduler corriendo en segundo plano.")
    else:
        logger.warning("APScheduler está desactivado en las variables de entorno.")