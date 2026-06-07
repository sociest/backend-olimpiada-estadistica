import csv
import io
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session

from app.modules.sistema.sistema_repository import SistemaRepository
from app.modules.sistema.sistema_model import AuditoriaModel, ActividadSistemaModel, TipoAccion, TipoModulo
from app.modules.sistema.sistema_schema import AuditoriaCreateDTO, ActividadSistemaCreateDTO
from app.modules.convocatorias.convocatoria_repository import ConvocatoriaRepository
from app.modules.inscripciones.inscripcion_repository import InscripcionRepository
from app.modules.avisos.aviso_repository import AvisoRepository
from app.modules.auth.auth_model import AdministradorModel
from app.modules.fases.fase_repository import FaseRepository
from app.modules.campanias.campania_repository import CampaniaRepository

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
        
    def _ensure_utc(self, dt: datetime) -> datetime:
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc) 
    
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
        
    def get_actividad_reciente(self, skip: int, limit: int):
        items, total = self.repository.get_actividad_reciente(skip, limit)
        
        mapped_items = []
        for row in items:
            mapped_items.append({
                "id_registro": row.id_registro,
                "tipo_registro": row.tipo_registro,
                "fecha": row.fecha,
                "descripcion": row.descripcion,
                "accion": row.accion.capitalize() if row.accion else None,
                "modulo": row.modulo,
                "titulo": row.titulo,
                "tipo_actividad": row.tipo_actividad
            })
            
        return mapped_items, total

    def get_eventos_proximos(
        self,
        page: int = 1,
        limit: int = 10
    ):

        now = datetime.now(timezone.utc)
        eventos = []

        conv_repo = ConvocatoriaRepository(self.db)
        fase_repo = FaseRepository(self.db)
        campania_repo = CampaniaRepository(self.db)

        convocatoria = conv_repo.get_convocatoria_principal()

        if convocatoria:

            if (
                convocatoria.fecha_inicio_inscripcion
                and convocatoria.fecha_inicio_inscripcion >= now
            ):
                eventos.append({
                    "tipo": "INSCRIPCION",
                    "titulo": "Inicio de inscripciones",
                    "descripcion": convocatoria.nombre_convocatoria,
                    "fecha": self._ensure_utc(convocatoria.fecha_inicio_inscripcion),
                    "referencia_id": convocatoria.id_convocatoria
                })

            if (
                convocatoria.fecha_fin_inscripcion
                and convocatoria.fecha_fin_inscripcion >= now
            ):
                eventos.append({
                    "tipo": "INSCRIPCION",
                    "titulo": "Cierre de inscripciones",
                    "descripcion": convocatoria.nombre_convocatoria,
                    "fecha": self._ensure_utc(convocatoria.fecha_fin_inscripcion),
                    "referencia_id": convocatoria.id_convocatoria
                })

            if (
                convocatoria.inicio_olimpiadas
                and convocatoria.inicio_olimpiadas >= now.date()
            ):
                eventos.append({
                    "tipo": "CONVOCATORIA",
                    "titulo": "Inicio de Olimpiadas",
                    "descripcion": convocatoria.nombre_convocatoria,
                    "fecha": self._ensure_utc(datetime.combine(
                        convocatoria.inicio_olimpiadas,
                        datetime.min.time(),
                        tzinfo=timezone.utc
                    )),
                    "referencia_id": convocatoria.id_convocatoria
                })

            if (
                convocatoria.fin_olimpiadas
                and convocatoria.fin_olimpiadas >= now.date()
            ):
                eventos.append({
                    "tipo": "CONVOCATORIA",
                    "titulo": "Fin de Olimpiadas",
                    "descripcion": convocatoria.nombre_convocatoria,
                    "fecha": self._ensure_utc(datetime.combine(
                        convocatoria.fin_olimpiadas,
                        datetime.min.time(),
                        tzinfo=timezone.utc
                    )),
                    "referencia_id": convocatoria.id_convocatoria
                })

        fases_preparacion, fases_prueba = (fase_repo.get_fases_proximas())

        for fase in fases_preparacion:

            if fase.fecha_inicio >= now:
                eventos.append({
                    "tipo": "PREPARACION",
                    "titulo": f"Inicio {fase.fase_base.nombre_fase}",
                    "descripcion": "Fase de preparación",
                    "fecha": self._ensure_utc(fase.fecha_inicio),
                    "referencia_id": fase.id_fase
                })

            if fase.fecha_fin >= now:
                eventos.append({
                    "tipo": "PREPARACION",
                    "titulo": f"Fin {fase.fase_base.nombre_fase}",
                    "descripcion": "Fase de preparación",
                    "fecha": self._ensure_utc(fase.fecha_fin),
                    "referencia_id": fase.id_fase
                })

        for fase in fases_prueba:

            eventos.append({
                "tipo": "PRUEBA",
                "titulo": fase.fase_base.nombre_fase,
                "descripcion": fase.lugar_realizacion,
                "fecha": self._ensure_utc(fase.fecha_realizacion),
                "referencia_id": fase.id_fase
            })

        campanias = campania_repo.get_programadas_futuras()

        for campania in campanias:
            eventos.append({
                "tipo": "EMAIL",
                "titulo": campania.nombre,
                "descripcion": campania.asunto,
                "fecha": self._ensure_utc(campania.fecha_programada),
                "referencia_id": campania.id_campania_email
            })

        eventos.sort(key=lambda evento: evento["fecha"])

        total = len(eventos)

        start = (page - 1) * limit
        end = start + limit

        items = eventos[start:end]

        return items, total