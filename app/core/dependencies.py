import httpx
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings
from app.core.exceptions import UnauthorizedError, BusinessRuleError
from app.core.security import decode_access_token
from app.db.database import get_db
from app.modules.auth.auth_repository import AuthRepository

bearer_scheme = HTTPBearer(auto_error=False)
limiter = Limiter(key_func=get_remote_address)

def get_current_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> int:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("No autorizado")

    payload = decode_access_token(credentials.credentials)
    admin_id = payload.get("sub")
    if admin_id is None:
        raise UnauthorizedError("Token invalido")

    repository = AuthRepository(db)
    admin = repository.get_admin_by_id(int(admin_id))
    if not admin:
        raise UnauthorizedError("No autorizado")

    return admin.id_administrador

async def verify_bot_protection(cf_turnstile_response: str, username_hp: str, client_ip: str | None = None) -> None:
    if username_hp:
        raise BusinessRuleError("Bot detectado")

    if not cf_turnstile_response:
        raise BusinessRuleError("Falta token de seguridad")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={
                "secret": settings.cloudflare_secret_key,
                "response": cf_turnstile_response,
                "remoteip": client_ip
            }
        )
        outcome = response.json()

    if not outcome.get("success"):
        raise BusinessRuleError("Validacion de seguridad fallida")