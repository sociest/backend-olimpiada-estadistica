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

MAX_PROFILE_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_PROFILE_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif"
}

class SupabaseStorageClient:
    def __init__(self):
        self.base_url = self._normalize_supabase_url(settings.supabase_url)
        self.service_role_key = settings.supabase_service_role_key
        self.bucket_materiales = settings.supabase_bucket_materiales
        self.bucket_perfiles = settings.supabase_bucket_perfiles
        self.client = self._create_client()

    def upload_material(self, content: bytes, filename: str, content_type: str | None) -> str:
        if not self.base_url or not self.service_role_key:
            raise BusinessRuleError("Supabase no esta configurado")

        if len(content) > MAX_MATERIAL_FILE_SIZE:
            raise BusinessRuleError("El archivo supera el limite de 40 MB")

        detected_content_type = content_type or mimetypes.guess_type(filename)[0]
        if not self._is_allowed_content_type(detected_content_type, allowed_types=ALLOWED_MATERIAL_CONTENT_TYPES):
            raise BusinessRuleError("Tipo de archivo no permitido")

        nombre_seguro = self._sanitizar_path(filename)
        storage_path = parse.quote(nombre_seguro)

        try:
            self.client.storage.from_(self.bucket_materiales).upload(
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

        return f"{self.base_url}/storage/v1/object/public/{self.bucket_materiales}/{storage_path}"

    def rename_file(self, old_url: str, new_filename: str) -> str:
        try:
            path_in_bucket = old_url.split(f"{self.bucket_materiales}/")[-1]
            decoded_old_path = parse.unquote(path_in_bucket)
            new_storage_path = parse.quote(self._sanitizar_path(new_filename))
            self.client.storage.from_(self.bucket_materiales).move(decoded_old_path, new_storage_path)
            return f"{self.base_url}/storage/v1/object/public/{self.bucket_materiales}/{new_storage_path}"
        except Exception as exc:
            raise BusinessRuleError(f"Error al renombrar archivo en Supabase: {str(exc)}")

    def delete_file(self, file_url: str):
        try:
            path_in_bucket = file_url.split(f"{self.bucket_materiales}/")[-1]
            decoded_path = parse.unquote(path_in_bucket)
            self.client.storage.from_(self.bucket_materiales).remove([decoded_path])
        except Exception:
            pass

        # ==================== MÉTODOS PARA PERFILES ====================
    def upload_profile(self, content: bytes, filename: str, content_type: str | None = None, user_id: str = None) -> str:
        if not self.base_url or not self.service_role_key:
            raise BusinessRuleError("Supabase no esta configurado")

        if len(content) > MAX_PROFILE_FILE_SIZE:
            raise BusinessRuleError(f"El archivo supera el limite de 5 MB (tamaño: {len(content) / 1024 / 1024:.2f} MB)")

        detected_content_type = content_type or mimetypes.guess_type(filename)[0]
        if not self._is_allowed_content_type(detected_content_type, allowed_types=ALLOWED_PROFILE_CONTENT_TYPES):
            raise BusinessRuleError("Tipo de archivo no permitido. Solo se aceptan imágenes JPEG, PNG, WEBP o GIF")

        extension = self._get_extension_from_filename(filename) or self._get_extension_from_content_type(detected_content_type)
        if not extension:
            extension = '.jpg'

        if user_id:
            unique_filename = f"{user_id}{extension}"
        else:
            unique_filename = f"{uuid.uuid4().hex}{extension}"

        storage_path = unique_filename

        try:
            self.client.storage.from_(self.bucket_perfiles).upload(
                storage_path,
                content,
                {
                    "content-type": detected_content_type or "image/jpeg",
                    "upsert": "true",
                },
            )
        except Exception as exc:
            detalle = str(exc) or "Error desconocido"
            raise BusinessRuleError(f"No se pudo subir la imagen de perfil a Supabase: {detalle}") from exc

        return f"{self.base_url}/storage/v1/object/public/{self.bucket_perfiles}/{storage_path}"

    def delete_profile(self, file_url: str):
        try:
            path_in_bucket = file_url.split(f"{self.bucket_perfiles}/")[-1]
            self.client.storage.from_(self.bucket_perfiles).remove([path_in_bucket])
        except Exception:
            pass

    def rename_profile(self, old_url: str, new_filename: str) -> str:
        try:
            path_in_bucket = old_url.split(f"{self.bucket_perfiles}/")[-1]
            new_storage_path = self._sanitizar_path(new_filename)
            self.client.storage.from_(self.bucket_perfiles).move(path_in_bucket, new_storage_path)
            return f"{self.base_url}/storage/v1/object/public/{self.bucket_perfiles}/{new_storage_path}"
        except Exception as exc:
            raise BusinessRuleError(f"Error al renombrar imagen de perfil: {str(exc)}")

    def get_profile_public_url(self, filename: str) -> str:
        return f"{self.base_url}/storage/v1/object/public/{self.bucket_perfiles}/{filename}"

    def profile_exists(self, filename: str) -> bool:
        try:
            res = self.client.storage.from_(self.bucket_perfiles).list(filename)
            return any(item['name'] == filename for item in res)
        except Exception:
            return False

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

    def _is_allowed_content_type(self, content_type: str | None, allowed_types: set) -> bool:
        if not content_type:
            return False
        return content_type in allowed_types

    def _get_extension_from_filename(self, filename: str) -> str:
        if not filename:
            return ""
        path = Path(filename)
        return path.suffix.lower() if path.suffix else ""

    def _get_extension_from_content_type(self, content_type: str | None) -> str:
        if not content_type:
            return ""
        mime_to_ext = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
            "image/gif": ".gif"
        }
        return mime_to_ext.get(content_type.lower(), "")

    def _sanitizar_path(self, path: str) -> str:
        import unicodedata, re

        segmentos = path.split("/")
        segmentos_limpios = []

        for segmento in segmentos:
            segmento = unicodedata.normalize("NFKD", segmento).encode("ascii", "ignore").decode("ascii")
            segmento = re.sub(r"[^a-zA-Z0-9_.\s-]", "_", segmento)
            segmento = re.sub(r"\s+", "_", segmento)
            segmento = re.sub(r"_{2,}", "_", segmento)
            segmento = segmento.strip("_")
            segmentos_limpios.append(segmento)
        return "/".join(segmentos_limpios)