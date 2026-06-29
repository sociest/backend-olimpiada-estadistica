import csv
import io
from datetime import date
from sqlalchemy.orm import Session
from app.core.exceptions import NotFoundError
from app.modules.estudiantes.estudiante_repository import EstudianteRepository
from app.modules.estudiantes.estudiante_schema import EstudianteCreateDTO, EstudianteUpdateDTO, EstudianteEstadoUpdateDTO
from app.modules.estudiantes.estudiante_model import EstudianteModel
from app.modules.personas.persona_model import PersonaModel
from app.modules.sistema.sistema_model import AuditoriaModel, TipoAccion, TipoModulo
from app.modules.sistema.sistema_repository import SistemaRepository
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape, A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
)
from reportlab.lib.styles import getSampleStyleSheet
class EstudianteService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = EstudianteRepository(db)
        self.sistema_repository = SistemaRepository(db)

    def crear_estudiante(self, data: EstudianteCreateDTO, current_admin_id: int):
        if not data.id_colegio :
            raise ValueError("El ID del colegio es requerido")
        if data.id_colegio <= 0:
            raise ValueError("El ID del colegio debe ser un número positivo")
        
        try:
            persona = PersonaModel(
                nombres=data.nombres,
                paterno=data.paterno,
                materno=data.materno
            )
            self.repository.create_persona(persona)
            
            estudiante = EstudianteModel(
                id_estudiante=persona.id_persona,
                id_colegio=data.id_colegio,
                carnet_identidad=data.carnet_identidad,
                curso=data.curso,
                nivel=data.nivel,
                fecha_nacimiento=data.fecha_nacimiento,
                rude=data.rude,
                telefono=data.telefono,
                correo=data.correo,
            )
            self.repository.create_estudiante(estudiante)
            self.db.commit()
            self.db.refresh(estudiante)
            self._auditar(
                current_admin_id,
                TipoAccion.CREAR,
                f"Estudiante creado {persona.nombres} {persona.paterno} CI {estudiante.carnet_identidad}",
            )
            return estudiante
        except Exception:
            self.db.rollback()
            raise

    def listar_estudiantes(self, page: int, limit: int, **filters):
        skip = (page - 1) * limit
        items, total = self.repository.list_estudiantes(skip=skip, limit=limit, **filters)
        return items, total

    def obtener_por_id(self, estudiante_id: int):
        estudiante = self.repository.get_by_id(estudiante_id)
        if not estudiante:
            raise NotFoundError("Estudiante no encontrado")
        return estudiante

    def actualizar_estudiante(self, estudiante_id: int, data: EstudianteUpdateDTO, current_admin_id: int):
        estudiante = self.obtener_por_id(estudiante_id)
        persona = self.repository.get_persona_by_id(estudiante_id)
        
        updates = data.model_dump(exclude_unset=True)
        
        for field in ("nombres", "paterno", "materno"):
            if field in updates:
                setattr(persona, field, updates[field])
                
        for field in ("id_colegio", "curso", "nivel", "rude", "telefono", "correo"):
            if field in updates:
                setattr(estudiante, field, updates[field])

        self.repository.update()
        self.db.refresh(estudiante)
        self._auditar(
            current_admin_id,
            TipoAccion.ACTUALIZAR,
            f"Estudiante actualizado {persona.nombres} {persona.paterno} CI {estudiante.carnet_identidad}",
        )
        return estudiante

    def cambiar_estado(self, estudiante_id: int, data: EstudianteEstadoUpdateDTO, current_admin_id: int):
        estudiante = self.obtener_por_id(estudiante_id)
        persona = self.repository.get_persona_by_id(estudiante_id)
        estado_anterior = persona.estado
        persona.estado = data.estado
        self.repository.update()
        self.db.refresh(estudiante)
        self._auditar(
            current_admin_id,
            TipoAccion.ACTUALIZAR,
            f"Estudiante {persona.nombres} {persona.paterno} CI {estudiante.carnet_identidad} cambio estado de {estado_anterior} a {data.estado}",
        )
        return estudiante

    def exportar_csv(self, ids: list[int]) -> str:
        estudiantes = self.repository.get_by_ids(ids)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "ID", "Carnet", "Nombres", "Paterno", "Materno", "F. Nacimiento", 
            "Edad", "RUDE", "Curso", "Nivel", "Colegio", "Turno", "Municipio", "Estado"
        ])
        
        today = date.today()
        
        for est in estudiantes:
            edad = today.year - est.fecha_nacimiento.year - ((today.month, today.day) < (est.fecha_nacimiento.month, est.fecha_nacimiento.day))
            nombre_colegio = est.colegio.nombre if est.colegio else str(est.id_colegio)
            municipio_colegio = est.colegio.municipio if est.colegio else "N/A"
            turno_colegio = est.colegio.turno if est.colegio else "N/A"
            rude_val = est.rude if est.rude else ""
            
            writer.writerow([
                est.id_estudiante, est.carnet_identidad, est.nombres, est.paterno, 
                est.materno, est.fecha_nacimiento, edad, rude_val, est.curso, 
                est.nivel, nombre_colegio, turno_colegio, municipio_colegio, est.estado
            ])
            
        return output.getvalue()

    def exportar_pdf(self, ids: list[int]) -> bytes:
        estudiantes = self.repository.get_by_ids(ids)

        buffer = io.BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            leftMargin=15,
            rightMargin=15,
            topMargin=20,
            bottomMargin=20
        )

        elements = []

        styles = getSampleStyleSheet()
        style = styles["BodyText"]
        style.fontName = "Helvetica"
        style.fontSize = 7
        style.leading = 8

        data = [[
            "Carnet",
            "Nombre Completo",
            "F. Nacimiento",
            "Edad",
            "RUDE",
            "Curso",
            "Nivel",
            "Colegio",
            "Turno",
            "Municipio"
        ]]

        today = date.today()

        for est in estudiantes:

            edad = (
                today.year
                - est.fecha_nacimiento.year
                - (
                    (today.month, today.day)
                    < (est.fecha_nacimiento.month, est.fecha_nacimiento.day)
                )
            )

            nombre_completo = f"{est.nombres} {est.paterno} {est.materno or ''}".strip()

            nombre_colegio = (
                est.colegio.nombre
                if est.colegio
                else str(est.id_colegio)
            )

            municipio = (
                est.colegio.municipio
                if est.colegio
                else "N/A"
            )

            turno = (
                est.colegio.turno
                if est.colegio
                else "N/A"
            )

            rude = est.rude or ""

            data.append([
                Paragraph(str(est.carnet_identidad), style),
                Paragraph(nombre_completo, style),
                Paragraph(str(est.fecha_nacimiento), style),
                Paragraph(str(edad), style),
                Paragraph(rude, style),
                Paragraph(str(est.curso), style),
                Paragraph(est.nivel, style),
                Paragraph(nombre_colegio, style),
                Paragraph(turno, style),
                Paragraph(municipio, style),
            ])

        # Ancho disponible
        page_width, _ = landscape(A4)
        available_width = (
            page_width
            - doc.leftMargin
            - doc.rightMargin
        )

        # Peso de cada columna
        weights = [
            1.4,  # Carnet
            2.8,  # Nombre
            1.5,  # Fecha
            0.8,  # Edad
            1.8,  # RUDE
            1.0,  # Curso
            1.3,  # Nivel
            3.2,  # Colegio
            1.2,  # Turno
            1.8,  # Municipio
        ]

        total = sum(weights)

        col_widths = [
            available_width * w / total
            for w in weights
        ]

        table = Table(
            data,
            colWidths=col_widths,
            repeatRows=1
        )

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4CAF50")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),

            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

            ('FONTSIZE', (0, 0), (-1, 0), 8),

            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),

            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),

            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))

        elements.append(table)
        doc.build(elements)

        return buffer.getvalue()

    def _auditar(self, current_admin_id: int, accion: TipoAccion, descripcion: str):
        self.sistema_repository.create_auditoria(
            AuditoriaModel(
                id_administrador=current_admin_id,
                accion=accion,
                modulo=TipoModulo.ESTUDIANTE,
                descripcion=descripcion,
            )
        )
