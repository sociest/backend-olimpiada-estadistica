import base64
import hashlib
import hmac
import json
import secrets
import re
from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.config import settings
from app.core.exceptions import UnauthorizedError, ValidationError


PASSWORD_HASH_ALGORITHM = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 260000


def validate_password_complexity(password: str) -> None:
    if len(password) < 8:
        raise ValidationError("La contrasena debe tener al menos 8 caracteres")
    if not re.search(r"[A-Z]", password):
        raise ValidationError(
            "La contrasena debe incluir al menos una letra mayuscula"
        )
    if not re.search(r"[a-z]", password):
        raise ValidationError(
            "La contrasena debe incluir al menos una letra minuscula"
        )
    if not re.search(r"[0-9]", password):
        raise ValidationError("La contrasena debe incluir al menos un numero")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_+\-=\[\]\\\/]', password):
        raise ValidationError(
            "La contrasena debe incluir al menos un caracter especial (!@#$...)"
        )

def hash_password(password: str) -> str:
    bcrypt_context = _get_bcrypt_context()
    if bcrypt_context:
        return bcrypt_context.hash(password)

    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_ITERATIONS,
    ).hex()
    return f"{PASSWORD_HASH_ALGORITHM}${PASSWORD_ITERATIONS}${salt}${digest}"


def verify_password(password: str, password_hash: str) -> bool:
    bcrypt_context = _get_bcrypt_context()
    if bcrypt_context and password_hash.startswith(("$2a$", "$2b$", "$2y$")):
        return bcrypt_context.verify(password, password_hash)

    try:
        algorithm, iterations, salt, expected_digest = password_hash.split("$", 3)
    except ValueError:
        return False

    if algorithm != PASSWORD_HASH_ALGORITHM:
        return False

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        int(iterations),
    ).hex()
    return hmac.compare_digest(digest, expected_digest)


def create_access_token(subject: int, expires_delta: timedelta | None = None) -> str:
    expires_at = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {"sub": str(subject), "exp": int(expires_at.timestamp())}
    return _encode_jwt(payload)


def decode_access_token(token: str) -> dict[str, Any]:
    payload = _decode_jwt(token)
    expires_at = payload.get("exp")
    if expires_at is None or int(expires_at) < int(datetime.now(timezone.utc).timestamp()):
        raise UnauthorizedError("Token expirado")
    return payload


def _encode_jwt(payload: dict[str, Any]) -> str:
    header = {"alg": settings.algorithm, "typ": "JWT"}
    encoded_header = _base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    encoded_payload = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
    signature = _sign(signing_input)
    return f"{encoded_header}.{encoded_payload}.{signature}"


def _decode_jwt(token: str) -> dict[str, Any]:
    try:
        encoded_header, encoded_payload, signature = token.split(".")
    except ValueError:
        raise UnauthorizedError("Token invalido")

    signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
    expected_signature = _sign(signing_input)
    if not hmac.compare_digest(signature, expected_signature):
        raise UnauthorizedError("Token invalido")

    try:
        header = json.loads(_base64url_decode(encoded_header))
        payload = json.loads(_base64url_decode(encoded_payload))
    except (json.JSONDecodeError, ValueError):
        raise UnauthorizedError("Token invalido")

    if header.get("alg") != settings.algorithm:
        raise UnauthorizedError("Token invalido")

    return payload


def _sign(signing_input: bytes) -> str:
    if settings.algorithm != "HS256":
        raise UnauthorizedError("Algoritmo JWT no soportado")
    digest = hmac.new(settings.secret_key.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return _base64url_encode(digest)


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _base64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _get_bcrypt_context():
    try:
        from passlib.context import CryptContext
    except ImportError:
        return None
    return CryptContext(schemes=["bcrypt"], deprecated="auto")
