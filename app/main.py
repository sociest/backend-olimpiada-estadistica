from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.exceptions import register_exception_handlers
from app.modules.auth.auth_router import router as auth_router
from app.modules.categorias.categoria_router import router as categoria_router
from app.modules.colegios.colegio_router import router as colegio_router
from app.modules.convocatorias.convocatoria_router import router as convocatoria_router
from app.modules.fases.fase_router import router as fase_router
from app.modules.materiales.material_router import router as material_router
from app.modules.personas.persona_router import router as persona_router


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
app.include_router(convocatoria_router)
app.include_router(categoria_router)
app.include_router(colegio_router)
app.include_router(fase_router)
app.include_router(material_router)
app.include_router(persona_router)
