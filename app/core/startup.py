from app.db.database import SessionLocal
from app.modules.auth.auth_model import AdministradorModel
from app.core.config import settings
from app.core.security import hash_password
import logging
import time
from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)

def create_initial_admin():
    max_attempts = 6
    base_delay = 1
    db = SessionLocal()
    
    try:
        for attempt in range(1, max_attempts + 1):
            try:
                admin_exists = db.query(AdministradorModel).first()

                if not admin_exists:
                    admin = AdministradorModel(
                        nombre=settings.first_admin_username,
                        correo=settings.first_admin_email,
                        contrasena=hash_password(settings.first_admin_password)
                    )
                    db.add(admin)
                    db.commit()
                    logger.info(f"Administrador inicial creado correctamente: {admin.nombre}")
                else:
                    logger.info("Administrador inicial ya existe")
                
                return

            except OperationalError as e:
                if attempt == max_attempts:
                    logger.error(f"Error definitivo al conectar con la BD: {e}")
                    raise
                
                delay = base_delay * (2 ** (attempt - 1))
                logger.warning(f"Intento {attempt}/{max_attempts} falló. Reintentando en {delay}s...")
                time.sleep(delay)
    finally:
        db.close()