import hashlib
import hmac

def verify_brevo_signature(payload_body: bytes, signature_header: str, secret: str) -> bool:
    if not signature_header or not secret:
        return False
    computed_signature = hmac.new(
        key=secret.encode("utf-8"),
        msg=payload_body,
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed_signature, signature_header)