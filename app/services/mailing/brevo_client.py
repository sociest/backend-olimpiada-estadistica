import httpx
from app.core.config import settings
from app.services.mailing.exceptions import BrevoAPIError

class BrevoClient:
    def __init__(self):
        self.api_key = settings.brevo_api_key
        self.base_url = settings.brevo_base_url
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def send_email(self, subject: str, html_content: str, to_email: str, to_name: str = None) -> dict:
        if not settings.brevo_enabled:
            return {"messageId": "mock-id-local-dev"}

        payload = {
            "sender": {"name": settings.brevo_sender_name, "email": settings.brevo_sender_email},
            "to": [{"email": to_email, "name": to_name}] if to_name else [{"email": to_email}],
            "replyTo": {"email": settings.brevo_reply_to},
            "subject": subject,
            "htmlContent": html_content
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/smtp/email", json=payload, headers=self.headers, timeout=settings.mailing_timeout_seconds)
            
            if response.status_code not in (201, 200, 202):
                raise BrevoAPIError(f"Brevo API Error {response.status_code}: {response.text}")
            
            return response.json()