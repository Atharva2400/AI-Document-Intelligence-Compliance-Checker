"""
storage_service.py
------------------
Supabase Storage integration for AI Document Intelligence.

Uploads original documents directly to Supabase private "documents" bucket.
Falls back to local-only storage gracefully if:
  - SUPABASE_ENABLED=false
  - Supabase credentials are missing
  - Supabase upload fails for any reason

Never exposes secrets in logs or API responses.
"""

import logging
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("storage_service")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [StorageService] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Configuration (read once at import time)
# ---------------------------------------------------------------------------

_SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ewmanzzpjjdzveuciuur.supabase.co").strip()
_SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY", "").strip()
_SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET_NAME", "documents").strip()
_SUPABASE_ENABLED = os.getenv("SUPABASE_ENABLED", "false").strip().lower() == "true"

# Direct Storage endpoint URL
_STORAGE_HOST = "https://ewmanzzpjjdzveuciuur.storage.supabase.co"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def upload_to_supabase(local_file_path: Path, unique_filename: str) -> dict:
    """
    Uploads the file at *local_file_path* to Supabase Storage under
    ``uploads/{unique_filename}``.

    Returns a metadata dict:
        {
            "provider": "supabase" | "local",
            "bucket": "<bucket_name>",
            "path": "uploads/<unique_filename>",
            "uploaded": True | False
        }

    This function NEVER raises — all Supabase errors are caught and logged.
    The caller can always continue with local-only processing.
    """
    storage_meta = {
        "provider": "local",
        "bucket": _SUPABASE_BUCKET,
        "path": f"uploads/{unique_filename}",
        "uploaded": False,
    }

    if not _SUPABASE_ENABLED:
        logger.info("SUPABASE_ENABLED=false — skipping Supabase upload, using local storage.")
        return storage_meta

    if not _SUPABASE_SECRET_KEY:
        logger.warning("Supabase secret key is not configured. Storage will use local fallback.")
        return storage_meta

    storage_path = f"uploads/{unique_filename}"

    try:
        ext = local_file_path.suffix.lower()
        mime_map = {
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".txt": "text/plain",
        }
        content_type = mime_map.get(ext, "application/octet-stream")

        with open(local_file_path, "rb") as f:
            file_bytes = f.read()

        url = f"{_STORAGE_HOST}/storage/v1/object/{_SUPABASE_BUCKET}/{storage_path}"
        headers = {
            "Authorization": f"Bearer {_SUPABASE_SECRET_KEY}",
            "apiKey": _SUPABASE_SECRET_KEY,
            "x-upsert": "true",
            "Content-Type": content_type,
        }

        import httpx
        response = httpx.post(url, headers=headers, content=file_bytes, timeout=15.0)

        if response.status_code in (200, 201):
            storage_meta["provider"] = "supabase"
            storage_meta["uploaded"] = True
            logger.info(f"Uploaded '{unique_filename}' to Supabase bucket '{_SUPABASE_BUCKET}' at path '{storage_path}'.")
        else:
            logger.warning(
                f"Supabase upload failed (HTTP {response.status_code}: {response.text[:120]}). "
                "Continuing with local storage."
            )

    except FileNotFoundError:
        logger.warning(f"Local file not found for Supabase upload: {local_file_path}. Skipping.")
    except Exception as exc:
        # Log type only — never log the exception message (may contain credentials)
        logger.warning(
            f"Supabase upload failed ({type(exc).__name__}: {str(exc)[:120]}). "
            "Continuing with local storage."
        )

    return storage_meta
