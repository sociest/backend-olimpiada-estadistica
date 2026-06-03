import mimetypes
import uuid
from pathlib import Path
from urllib import parse

from app.core.config import settings
from app.core.exceptions import BusinessRuleError

MAX_MATERIAL_FILE_SIZE = 40 * 1024 * 1024
ALLOWED_MATERIAL_CONTENT_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "image/jpeg",
    "image/jpeg",
    "image/png",
    "image/svg+xml"
}


class SupabaseStorageClient:
    def __init__(self):
        self.base_url = self._normalize_supabase_url(settings.supabase_url)
        self.service_role_key = settings.supabase_service_role_key
        self.bucket = settings.supabase_bucket_materiales
        self.client = self._create_client()

    def upload_material(self, content: bytes, filename: str, content_type: str | None) -> str:
        if not self.base_url or not self.service_role_key:
            raise BusinessRuleError("Supabase no esta configurado")

        if len(content) > MAX_MATERIAL_FILE_SIZE:
            raise BusinessRuleError("El archivo supera el limite de 40 MB")

        detected_content_type = content_type or mimetypes.guess_type(filename)[0]
        if not self._is_allowed_content_type(detected_content_type):
            raise BusinessRuleError("Tipo de archivo no permitido")

        storage_path = parse.quote(filename)

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
            raise BusinessRuleError(f"No se pudo subir el archivo a Supabase: {detalle}") from exc

        return f"{self.base_url}/storage/v1/object/public/{self.bucket}/{storage_path}"

    def rename_file(self, old_url: str, new_filename: str) -> str:
        try:
            path_in_bucket = old_url.split(f"{self.bucket}/")[-1]
            decoded_old_path = parse.unquote(path_in_bucket)
            new_storage_path = parse.quote(new_filename)
            self.client.storage.from_(self.bucket).move(decoded_old_path, new_storage_path)
            return f"{self.base_url}/storage/v1/object/public/{self.bucket}/{new_storage_path}"
        except Exception as exc:
            raise BusinessRuleError(f"Error al renombrar archivo en Supabase: {str(exc)}")

    def delete_file(self, file_url: str):
        try:
            path_in_bucket = file_url.split(f"{self.bucket}/")[-1]
            decoded_path = parse.unquote(path_in_bucket)
            self.client.storage.from_(self.bucket).remove([decoded_path])
        except Exception:
            pass

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
        return content_type in ALLOWED_MATERIAL_CONTENT_TYPES