import mimetypes
import uuid
from pathlib import Path
from urllib import parse

from app.core.config import settings
from app.core.exceptions import BusinessRuleError


MAX_MATERIAL_FILE_SIZE = 25 * 1024 * 1024
ALLOWED_MATERIAL_CONTENT_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


class SupabaseStorageClient:
    def __init__(self):
        self.base_url = self._normalize_supabase_url(settings.supabase_url)
        self.service_role_key = settings.supabase_service_role_key
        self.bucket = settings.supabase_bucket_materiales
        self.client = self._create_client()

    def upload_material(self, content: bytes, filename: str, tipo_material: str, content_type: str | None) -> str:
        if not self.base_url or not self.service_role_key:
            raise BusinessRuleError("Supabase no esta configurado")

        if len(content) > MAX_MATERIAL_FILE_SIZE:
            raise BusinessRuleError("El archivo supera el limite de 25 MB")

        detected_content_type = content_type or mimetypes.guess_type(filename)[0]
        if not self._is_allowed_content_type(detected_content_type):
            raise BusinessRuleError("Tipo de archivo no permitido")

        safe_filename = f"{uuid.uuid4().hex}_{self._safe_filename(filename)}"
        storage_path = f"{tipo_material}/{safe_filename}"

        try:
            self.client.storage.from_(self.bucket).upload(
                storage_path,
                content,
                {
                    "content-type": detected_content_type or "application/octet-stream",
                    "upsert": "true",
                },
            )
        except Exception as exc:
            detalle = str(exc) or "Error desconocido"
            raise BusinessRuleError(
                f"No se pudo subir el archivo a Supabase: {detalle}"
            ) from exc

        encoded_path = parse.quote(storage_path)
        return f"{self.base_url}/storage/v1/object/public/{self.bucket}/{encoded_path}"

    def _create_client(self):
        try:
            from supabase import create_client
        except ImportError as exc:
            raise BusinessRuleError("SDK de Supabase no instalado") from exc
        return create_client(self.base_url, self.service_role_key)

    def _normalize_supabase_url(self, url: str) -> str:
        clean_url = url.rstrip("/")
        if clean_url.endswith("/rest/v1"):
            clean_url = clean_url[: -len("/rest/v1")]
        return clean_url

    def _is_allowed_content_type(self, content_type: str | None) -> bool:
        if not content_type:
            return False
        return content_type in ALLOWED_MATERIAL_CONTENT_TYPES or content_type.startswith("image/") or content_type.startswith("video/")

    def _safe_filename(self, filename: str) -> str:
        name = Path(filename).name.replace(" ", "_")
        return name or "material"

    def upload_file(self, content: bytes, filename: str, folder: str, content_type: str = None) -> str:
        detected_type = content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
        safe_filename = f"{uuid.uuid4().hex}_{filename.replace(' ', '_')}"
        storage_path = f"{folder}/{safe_filename}"
        
        self.client.storage.from_(self.bucket).upload(
            storage_path, content, {"content-type": detected_type, "upsert": "true"}
        )
        return f"{self.base_url}/storage/v1/object/public/{self.bucket}/{parse.quote(storage_path)}"

    def delete_file(self, file_url: str):
        try:
            path_in_bucket = file_url.split(f"{self.bucket}/")[-1]
            decoded_path = parse.unquote(path_in_bucket)
            self.client.storage.from_(self.bucket).remove([decoded_path])
        except Exception:
            pass