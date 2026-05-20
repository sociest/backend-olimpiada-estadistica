from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.exceptions import register_exception_handlers
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


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_exception_handlers(app)

app.include_router(auth_router)
app.include_router(aviso_router)
app.include_router(convocatoria_router)
app.include_router(categoria_router)
app.include_router(colegio_router)
app.include_router(contacto_router)
app.include_router(fase_router)
app.include_router(estudiante_router)
app.include_router(inscripcion_router)
app.include_router(material_router)
app.include_router(persona_router)
app.include_router(public_router)
