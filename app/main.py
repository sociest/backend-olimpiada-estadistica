from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.dependencies import limiter
from app.core.exceptions import register_exception_handlers
from app.modules.administradores.administrador_router import router as administrador_router
from app.modules.auth.auth_router import router as auth_router
from app.modules.avisos.aviso_router import router as aviso_router
from app.modules.categorias.categoria_router import router as categoria_router
from app.modules.colegios.colegio_router import router as colegio_router
from app.modules.contactos.contacto_router import router as contacto_router
from app.modules.convocatorias.convocatoria_router import router as convocatoria_router
from app.modules.fases.fase_router import router as fase_router
from app.modules.estudiantes.estudiante_router import router as estudiante_router
from app.modules.inscripciones.inscripcion_router import router as inscripcion_router
from app.modules.materiales.material_router import router as material_router
from app.modules.personas.persona_router import router as persona_router
from app.modules.public_bff.public_router import router as public_router
from app.modules.campanias.campania_router import router as campanias_router
from app.modules.email_logs.email_log_router import router as email_logs_router
from contextlib import asynccontextmanager
from app.core.startup import create_initial_admin
from app.modules.resultados.resultado_router import router as resultados_router
import logging
from app.core.config import settings
from app.scheduler.scheduler import shutdown_scheduler, start_scheduler
from app.modules.sistema.sistema_router import router as sistema_router

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("apscheduler").setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    create_initial_admin()
    
    if settings.scheduler_enabled:
        start_scheduler()
        logger.info(
            "\n\n\t\tAPScheduler iniciado correctamente\n\n"
        )
    else:
        logger.warning(
            "\n\n\t\tAPScheduler deshabilitado\n\n"
        )
    yield
    if settings.scheduler_enabled:
        shutdown_scheduler()
        logger.info(
            "\n\n\t\tAPScheduler detenido\n\n"
        )
        


app = FastAPI(
    title="Olimpiada Paceña de Estadística API",
    version="1.0.0",
    lifespan=lifespan
)
app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url]if hasattr(settings, 'frontend_url') else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
register_exception_handlers(app)

API_PREFIJO_BASE = "/api/v1"
API_PREFIJO_PUBLIC = "/api/public/v1"

app.include_router(auth_router, prefix=API_PREFIJO_BASE)
app.include_router(administrador_router, prefix=API_PREFIJO_BASE)
app.include_router(aviso_router, prefix=API_PREFIJO_BASE)
app.include_router(convocatoria_router, prefix=API_PREFIJO_BASE)
app.include_router(categoria_router, prefix=API_PREFIJO_BASE)
app.include_router(colegio_router, prefix=API_PREFIJO_BASE)
app.include_router(contacto_router, prefix=API_PREFIJO_BASE)
app.include_router(fase_router, prefix=API_PREFIJO_BASE)
app.include_router(estudiante_router, prefix=API_PREFIJO_BASE)
app.include_router(inscripcion_router, prefix=API_PREFIJO_BASE)
app.include_router(material_router, prefix=API_PREFIJO_BASE)
app.include_router(persona_router, prefix=API_PREFIJO_BASE)
app.include_router(public_router, prefix=API_PREFIJO_PUBLIC)
app.include_router(campanias_router, prefix=API_PREFIJO_BASE)
app.include_router(email_logs_router, prefix=API_PREFIJO_BASE)
app.include_router(resultados_router, prefix=API_PREFIJO_BASE)
app.include_router(sistema_router, prefix=API_PREFIJO_BASE)

@app.get(API_PREFIJO_BASE)
def root():
    return {"status": "ok", "message": "API Operativa"}
