from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from app.scheduler.jobs.email_jobs import process_scheduled_campaigns, send_pending_emails, finalize_campaigns
from app.core.config import settings

jobstores = {
    'default': MemoryJobStore()
}

scheduler = AsyncIOScheduler(jobstores=jobstores, timezone=settings.scheduler_timezone)

def start_scheduler():
    if settings.scheduler_enabled:
        scheduler.add_job(process_scheduled_campaigns, 'interval', minutes=1, id='process_campaigns', replace_existing=True)
        scheduler.add_job(send_pending_emails, 'interval', minutes=settings.mailing_interval_minutes, id='send_emails', replace_existing=True)
        scheduler.add_job(finalize_campaigns, 'interval', minutes=2, id='finalize_campaigns', replace_existing=True)
        scheduler.start()