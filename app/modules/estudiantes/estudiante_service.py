import csv
import io
from datetime import date
from sqlalchemy.orm import Session
from app.core.exceptions import NotFoundError
from app.modules.estudiantes.estudiante_repository import EstudianteRepository
from app.modules.estudiantes.estudiante_schema import EstudianteCreateDTO, EstudianteUpdateDTO, EstudianteEstadoUpdateDTO
from app.modules.estudiantes.estudiante_model import EstudianteModel
from app.modules.personas.persona_model import PersonaModel
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

class EstudianteService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = EstudianteRepository(db)

    def crear_estudiante(self, data: EstudianteCreateDTO):
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

    def actualizar_estudiante(self, estudiante_id: int, data: EstudianteUpdateDTO):
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
        return estudiante

    def cambiar_estado(self, estudiante_id: int, data: EstudianteEstadoUpdateDTO):
        estudiante = self.obtener_por_id(estudiante_id)
        persona = self.repository.get_persona_by_id(estudiante_id)
        persona.estado = data.estado
        self.repository.update()
        self.db.refresh(estudiante)
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
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
        elements = []
        
        data = [["Carnet", "Nombre Completo", "F. Nacimiento", "Edad", "RUDE", "Curso", "Nivel", "Colegio", "Turno", "Municipio"]]
        today = date.today()
        
        for est in estudiantes:
            edad = today.year - est.fecha_nacimiento.year - ((today.month, today.day) < (est.fecha_nacimiento.month, est.fecha_nacimiento.day))
            nombre_completo = f"{est.nombres} {est.paterno} {est.materno or ''}".strip()
            nombre_colegio = est.colegio.nombre if est.colegio else str(est.id_colegio)
            municipio_colegio = est.colegio.municipio if est.colegio else "N/A"
            turno_colegio = est.colegio.turno if est.colegio else "N/A"
            rude_val = est.rude if est.rude else ""
            
            data.append([
                est.carnet_identidad, nombre_completo, str(est.fecha_nacimiento), str(edad), 
                rude_val, str(est.curso), est.nivel, nombre_colegio, turno_colegio, municipio_colegio
            ])
            
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4CAF50")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('WORDWRAP', (0, 0), (-1, -1), True)
        ]))
        
        elements.append(table)
        doc.build(elements)
        return buffer.getvalue()