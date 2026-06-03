"""Publisher agent: subir videos a plataformas.

Implementa un uploader para YouTube (OAuth2) y stubs para X, Facebook y TikTok.
Requiere `google-api-python-client` y `google-auth-oauthlib` instalados.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import List, Optional

logger = logging.getLogger(__name__)

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
except Exception:  # pragma: no cover - optional deps
    InstalledAppFlow = None
    Credentials = None
    Request = None
    build = None
    MediaFileUpload = None

YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]


def _ensure_google_libs():
    if build is None:
        raise RuntimeError("Dependencias de Google no están instaladas. Instale google-api-python-client y google-auth-oauthlib")


def get_youtube_credentials(client_secrets_file: str = "client_secrets.json", credentials_path: str = "youtube_credentials.json") -> Credentials:
    """Obtiene credenciales para la API de YouTube usando OAuth2 de tipo 'InstalledAppFlow'.

    - `client_secrets_file`: archivo JSON con client_id/client_secret (Google Cloud Console)
    - `credentials_path`: ruta donde se guardará el token serializado (JSON)
    """
    _ensure_google_libs()

    creds = None
    if os.path.exists(credentials_path):
        try:
            creds = Credentials.from_authorized_user_file(credentials_path, YOUTUBE_SCOPES)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None

    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, YOUTUBE_SCOPES)
        creds = flow.run_console()
        # guardar credenciales
        with open(credentials_path, "w", encoding="utf-8") as fh:
            fh.write(creds.to_json())

    return creds


def upload_to_youtube(
    video_file: str,
    title: str,
    description: str,
    tags: Optional[List[str]] = None,
    categoryId: str = "22",
    privacyStatus: str = "private",
    publishAt: Optional[datetime] = None,
    client_secrets_file: str = "client_secrets.json",
    credentials_path: str = "youtube_credentials.json",
):
    """Sube un video a YouTube.

    Si `publishAt` se proporciona, `privacyStatus` será forzado a 'private' y se usará
    el campo `publishAt` (RFC3339) para programar la publicación.
    Devuelve la respuesta del endpoint `videos.insert`.
    """
    _ensure_google_libs()

    creds = get_youtube_credentials(client_secrets_file=client_secrets_file, credentials_path=credentials_path)
    service = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
            "categoryId": categoryId,
        },
        "status": {
            "privacyStatus": privacyStatus,
        },
    }

    if publishAt:
        # YouTube requires 'publishAt' in RFC3339 and privacyStatus 'private'
        if publishAt.tzinfo is None:
            publish_at_str = publishAt.isoformat() + "Z"
        else:
            publish_at_str = publishAt.isoformat()
        body["status"]["privacyStatus"] = "private"
        body["status"]["publishAt"] = publish_at_str

    media = MediaFileUpload(video_file, chunksize=-1, resumable=True, mimetype="video/*")
    request = service.videos().insert(part=",".join(body.keys()), body=body, media_body=media)

    response = None
    try:
        logger.info("Iniciando subida de %s", video_file)
        status, response = request.next_chunk()
        while status is not None:
            logger.info("Progreso de subida %d%%", int(status.progress() * 100))
            status, response = request.next_chunk()
    except Exception as exc:
        logger.exception("Error subiendo a YouTube: %s", exc)
        raise

    logger.info("Subida completada. Video ID: %s", response.get("id") if response else "(sin respuesta)")
    return response


def upload_to_x(video_file: str, text: str, credentials: Optional[dict] = None):
    """Stub para subir video a X (Twitter). Implementación pendiente.

    Sugerencia: usar la API de X (v2/ads) o endpoints de medios con OAuth1.0a para cargas de video.
    """
    logger.warning("upload_to_x no implementado. Recibido: %s", video_file)
    raise NotImplementedError("upload_to_x no implementado. Se requiere integración con la API de X/Twitter")


def upload_to_facebook(video_file: str, message: str, access_token: Optional[str] = None):
    logger.warning("upload_to_facebook no implementado. Recibido: %s", video_file)
    raise NotImplementedError("upload_to_facebook no implementado. Use facebook-sdk o Graph API para uploads de video")


def upload_to_tiktok(video_file: str, caption: str, credentials: Optional[dict] = None):
    logger.warning("upload_to_tiktok no implementado. Recibido: %s", video_file)
    raise NotImplementedError("upload_to_tiktok no implementado. TikTok requiere API de partners o soluciones de terceros")


__all__ = [
    "upload_to_youtube",
    "upload_to_x",
    "upload_to_facebook",
    "upload_to_tiktok",
    "get_youtube_credentials",
]
def publish_to_youtube(video_path, title, description):
    # Integrate YouTube Data API here
    print(f'Publish {video_path} to YouTube with title: {title}')

def publish_to_x(video_path, text):
    # Integrate X/Twitter upload here
    print(f'Publish {video_path} to X with text: {text}')

if __name__ == '__main__':
    print('publisher stub')
