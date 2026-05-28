import os
from jinja2 import Environment, FileSystemLoader, select_autoescape

class EmailRenderer:
    def __init__(self):
        template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates", "email")
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def render_campania(self, title: str, asunto: str, usuario: str, contenido_mensaje: str, contenido_secundario: str = "", enlaces: list = None) -> str:
        template = self.env.get_template("campania.html")
        return template.render(
            title=title,
            asunto=asunto,
            usuario=usuario,
            contenido_mensaje=contenido_mensaje,
            contenido_secundario=contenido_secundario,
            enlaces=enlaces or []
        )