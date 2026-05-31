import csv
import io
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from app.modules.sistema.sistema_repository import SistemaRepository
from app.modules.sistema.sistema_model import AuditoriaModel, ActividadSistemaModel, TipoAccion, TipoModulo
from app.modules.sistema.sistema_schema import AuditoriaCreateDTO, ActividadSistemaCreateDTO
from app.modules.convocatorias.convocatoria_repository import ConvocatoriaRepository
from app.modules.inscripciones.inscripcion_repository import InscripcionRepository
from app.modules.avisos.aviso_repository import AvisoRepository
from app.modules.auth.auth_model import AdministradorModel


class SistemaService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = SistemaRepository(db)

    def _map_auditoria(self, audit: AuditoriaModel, admin: AdministradorModel) -> dict:
        return {
            "id_auditoria": audit.id_auditoria,
            "id_administrador": audit.id_administrador,
            "admin_nombre": admin.nombre,
            "accion": audit.accion.value.capitalize(),
            "descripcion": audit.descripcion,
            "modulo": audit.modulo,
            "fecha": audit.fecha
        }

    def get_auditorias(self, skip: int, limit: int, fecha_start, fecha_end, modulo, accion, busqueda):
        items, total = self.repository.get_auditorias(skip, limit, fecha_start, fecha_end, modulo, accion, busqueda)
        mapped_items = [self._map_auditoria(audit, admin) for audit, admin in items]
        return mapped_items, total

    def get_auditoria_reducida(self, limit: int = 10) -> List[dict]:
        items, _ = self.repository.get_auditorias(0, limit, None, None, None, None, None)
        return [
            {
                "admin_nombre": admin.nombre,
                "modulo": audit.modulo,
                "accion": audit.accion.value.capitalize()
            }
            for audit, admin in items
        ]

    def exportar_csv(self, fecha_start: datetime, fecha_end: datetime) -> str:
        items = self.repository.get_auditorias_by_rango(fecha_start, fecha_end)
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID Auditoria", "Administrador", "Accion", "Modulo", "Descripcion", "Fecha"])
        
        for audit, admin in items:
            writer.writerow([
                audit.id_auditoria,
                admin.nombre,
                audit.accion.value.capitalize(),
                audit.modulo.value if audit.modulo else "",
                audit.descripcion or "",
                audit.fecha.strftime("%Y-%m-%d %H:%M:%S")
            ])
            
        return output.getvalue()

    def create_auditoria(self, id_administrador: int, accion: TipoAccion, modulo: TipoModulo, descripcion: Optional[str] = None):
        nueva_auditoria = AuditoriaModel(
            id_administrador=id_administrador,
            accion=accion,
            modulo=modulo,
            descripcion=descripcion
        )
        return self.repository.create_auditoria(nueva_auditoria)

    def get_actividades(self, skip: int, limit: int):
        items, total = self.repository.get_actividades(skip, limit)
        return items, total

    def create_actividad(self, data: ActividadSistemaCreateDTO):
        nueva_actividad = ActividadSistemaModel(
            tipo=data.tipo,
            titulo=data.titulo,
            descripcion=data.descripcion
        )
        return self.repository.create_actividad(nueva_actividad)

    def get_admin_dashboard(self) -> dict:
        conv_repo = ConvocatoriaRepository(self.db)
        insc_repo = InscripcionRepository(self.db)
        aviso_repo = AvisoRepository(self.db)

        principal = conv_repo.get_convocatoria_principal()
        
        stats = {"total": 0, "aprobados": 0, "pendientes": 0}
        convocatoria_activa = None
        
        if principal:
            stats = insc_repo.get_estadisticas_inscripcion(principal.id_convocatoria)
            convocatoria_activa = {
                "id_convocatoria": principal.id_convocatoria,
                "nombre_convocatoria": principal.nombre_convocatoria
            }

        avisos_visibles = aviso_repo.count_visibles()

        return {
            "convocatoria_activa": convocatoria_activa,
            "inscripciones": stats,
            "avisos_visibles": avisos_visibles
        }