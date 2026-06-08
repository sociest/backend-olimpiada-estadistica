from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.config import settings
from app.core.dependencies import get_current_admin
from app.db.database import get_db
from app.modules.email_logs.email_log_schema import EmailLogResponseDTO, EmailLogCompletoResponseDTO
from app.modules.email_logs.email_log_service import EmailLogService
from app.modules.email_logs.email_log_model import EmailLog, EstadoEmail, TipoEmail
from app.core.responses import ResponseBase, PaginatedResponse, PaginationMeta
from app.services.mailing.utils import verify_brevo_signature
import logging

router = APIRouter(prefix="/email-logs", tags=["email_logs"])
logger = logging.getLogger(__name__)

@router.get("/", response_model=PaginatedResponse[EmailLogResponseDTO])
def listar_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    tipo: Optional[TipoEmail] = None,
    estado: Optional[EstadoEmail] = None,
    id_campania: Optional[int] = None,
    es_estudiante: Optional[bool] = None,
    es_contacto: Optional[bool] = None,
    es_campania: Optional[bool] = None,
    busqueda: Optional[str] = None,
    creacion_start: Optional[datetime] = None,
    creacion_end: Optional[datetime] = None,
    envio_start: Optional[datetime] = None,
    envio_end: Optional[datetime] = None,
    intento_start: Optional[datetime] = None,
    intento_end: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_admin_id: int = Depends(get_current_admin)
):
    service = EmailLogService(db)
    items, total = service.listar_logs(
        page, limit, tipo=tipo, estado=estado, id_campania=id_campania,
        es_estudiante=es_estudiante, es_contacto=es_contacto, es_campania=es_campania,
        busqueda=busqueda, creacion_start=creacion_start, creacion_end=creacion_end,
        envio_start=envio_start, envio_end=envio_end,
        intento_start=intento_start, intento_end=intento_end
    )
    total_pages = (total + limit - 1) // limit
    return PaginatedResponse(
        success=True, message="Logs listados",
        data={"items": items, "meta": PaginationMeta(page=page, limit=limit, total=total, total_pages=total_pages)}
    )

@router.get("/{id}", response_model=ResponseBase[EmailLogCompletoResponseDTO])
def obtener_log_por_id(
    id: int, 
    db: Session = Depends(get_db), 
    current_admin_id: int = Depends(get_current_admin)
):
    service = EmailLogService(db)
    log = service.obtener_por_id(id)
    return ResponseBase(success=True, message="Log obtenido correctamente", data=log)

@router.post("/reintentar-fallidos")
def reintentar_fallidos(db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = EmailLogService(db)
    afectados = service.reintentar_fallidos(current_admin_id)
    return ResponseBase(success=True, message=f"{afectados} correos pasados a PENDIENTE", data=None)

@router.post("/{id}/reintentar", response_model=ResponseBase[EmailLogResponseDTO])
def reintentar_un_fallido(id: int, db: Session = Depends(get_db), current_admin_id: int = Depends(get_current_admin)):
    service = EmailLogService(db)
    log = service.reintentar_fallido(id, current_admin_id)
    return ResponseBase(success=True, message="El correo ha sido encolado para reintento", data=log)

@router.post("/brevo-webhook")
async def brevo_webhook(request: Request, db: Session = Depends(get_db)):
    payload_body = await request.body()
    signature_header = request.headers.get("X-Brevo-Webhook-Signature", "")

    if not verify_brevo_signature(payload_body, signature_header, settings.brevo_webhook_secret):
        logger.warning("Webhook con firma inválida recibido")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Firma inválida")

    payload = await request.json()
    for event in payload.get("events", []):
        message_id = event.get("messageId")
        event_type = event.get("event")
        reason = event.get("reason", "")

        log = db.query(EmailLog).filter_by(brevo_message_id=message_id).first()
        if log:
            if event_type == "delivered":
                pass
            elif event_type in ("hard_bounce", "blocked", "invalid_email", "error", "rejected"):
                log.estado = EstadoEmail.FALLIDO
                log.error = reason
            elif event_type == "soft_bounce":
                log.estado = EstadoEmail.FALLIDO  # o mantenelo PENDIENTE según tu lógica
                log.error = reason
            db.commit()
            logger.info(f"EmailLog {log.id_email_log} actualizado a {log.estado} por webhook ({event_type})")
        else:
            logger.warning(f"No se encontró EmailLog para messageId {message_id}")

    return {"status": "ok"}