import csv
from io import StringIO, BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER

from app.modules.resultados.resultado_repository import ResultadoRepository
from app.core.exceptions import NotFoundError

class ExporterService:
    def __init__(self, db):
        self.repository = ResultadoRepository(db)

    def _get_context(self, id_fase_prueba: int):
        context = self.repository.get_fase_context_for_export(id_fase_prueba)
        if not context:
            raise NotFoundError("No se encontraron datos para esta fase.")
        return context

    def export_csv(self, id_fase_prueba: int, estado_aprobacion: str, incluir_nombres: bool):
        datos = self.repository.get_export_data(id_fase_prueba, estado_aprobacion)
        
        output = StringIO()
        writer = csv.writer(output)

        if incluir_nombres:
            writer.writerow(["carnet_identidad", "nombres", "paterno", "materno", "resultado"])
            for r in datos:
                writer.writerow([r.carnet_identidad, r.nombres, r.paterno, r.materno, r.resultado])
        else:
            writer.writerow(["carnet_identidad", "resultado"])
            for r in datos:
                writer.writerow([r.carnet_identidad, r.resultado])

        output.seek(0)
        return output

    def export_pdf(self, id_fase_prueba: int, estado_aprobacion: str, incluir_nombres: bool):
        fase_prueba, fase_base, categoria, convocatoria = self._get_context(id_fase_prueba)
        datos = self.repository.get_export_data(id_fase_prueba, estado_aprobacion)

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        elements = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'TitleCenter', 
            parent=styles['Normal'], 
            alignment=TA_CENTER, 
            fontSize=12, 
            spaceAfter=6, 
            fontName='Helvetica-Bold'
        )
        subtitle_style = ParagraphStyle(
            'SubCenter', 
            parent=styles['Normal'], 
            alignment=TA_CENTER, 
            fontSize=10, 
            spaceAfter=4,
            fontName='Helvetica'
        )

        elements.append(Paragraph(f"{convocatoria.nombre_convocatoria} {convocatoria.gestion}", title_style))
        elements.append(Paragraph("OLIMPIADA PACEÑA DE ESTADISTICA", title_style))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("UNIVERSIDAD MAYOR DE SAN ANDRES", subtitle_style))
        elements.append(Paragraph("FACULTAD DE CIENCIAS PURAS Y NATURALES", subtitle_style))
        elements.append(Paragraph("CARRERA DE ESTADISTICA", subtitle_style))
        elements.append(Spacer(1, 15))
        
        elements.append(Paragraph(f"{categoria.nombre_categoria} - CURSO {categoria.curso} {categoria.nivel.value}", title_style))
        elements.append(Paragraph(f"{fase_base.nombre_fase}", title_style))
        elements.append(Spacer(1, 20))

        if incluir_nombres:
            table_data = [["CI", "PATERNO", "MATERNO", "NOMBRES", "RESULTADO"]]
            col_widths = [70, 100, 100, 120, 70]
            for r in datos:
                table_data.append([r.carnet_identidad, r.paterno, r.materno, r.nombres, r.resultado])
        else:
            table_data = [["CARNET DE IDENTIDAD", "RESULTADO"]]
            col_widths = [150, 100]
            for r in datos:
                table_data.append([r.carnet_identidad, r.resultado])

        t = Table(table_data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#D3D3D3")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(t)
        doc.build(elements)
        buffer.seek(0)
        return buffer