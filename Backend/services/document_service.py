"""
document_service.py
-------------------
All business logic lives here — kept completely separate from routing.
When you add real document extraction (Phase 2) you only touch this file.

Current behaviour  : returns mock data.
Future behaviour   : extract text → call Vertex AI → run compliance engine.
"""

import os
import time
import copy
import shutil
from datetime import datetime
from pathlib import Path

from fastapi import UploadFile, HTTPException

from data.mock_analysis import MOCK_DATA, SUPPORTED_DEMO_TYPES

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024   # 50 MB


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _validate_extension(filename: str) -> None:
    """Raise 400 if the file extension is not in the allowed set."""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type '{ext}'. "
                f"Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            ),
        )


def _validate_size(file: UploadFile) -> None:
    """
    Raise 413 if the file is too large.
    NOTE: UploadFile.size is available only in recent FastAPI/Starlette versions.
    We do a safe check here.
    """
    if hasattr(file, "size") and file.size and file.size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024*1024)} MB.",
        )


def _save_file(file: UploadFile) -> Path:
    """
    Temporarily persist the uploaded file to the uploads/ directory.
    Returns the path where it was saved.
    In Phase 2 this would stream to Google Cloud Storage instead.
    """
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Use a timestamp prefix to avoid collisions
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_name = f"{timestamp}_{file.filename}"
    dest = UPLOAD_DIR / safe_name

    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    return dest


def _guess_doc_type(filename: str) -> str:
    """
    Naively guess the document type from the filename so we can choose
    the right mock response.  Phase 2 replaces this with Vertex AI classification.
    """
    name_lower = filename.lower()
    if any(k in name_lower for k in ("nda", "non-disclosure", "nondisclosure", "confidential")):
        return "nda"
    if any(k in name_lower for k in ("vendor", "service", "supplier", "procurement")):
        return "vendor"
    # Default to employment (most common demo)
    return "employment"


def _build_response(doc_type: str, document_name: str) -> dict:
    """
    Deep-copy the mock payload, inject real-time metadata, and return it.
    Deep copy ensures each API call gets its own independent dict.
    """
    payload = copy.deepcopy(MOCK_DATA[doc_type])
    payload["document_name"] = document_name
    payload["analyzed_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    return payload


# ─────────────────────────────────────────────────────────────────────────────
# Public service functions  (called by route handlers in main.py)
# ─────────────────────────────────────────────────────────────────────────────

def analyze_uploaded_document(file: UploadFile) -> dict:
    """
    Full pipeline for a user-uploaded document:
      1. Validate extension
      2. Validate size
      3. Save to uploads/
      4. (Phase 2) Extract text → classify → call AI → run compliance engine
      5. Return mock analysis matched to detected document type

    Returns a dict that matches the AnalysisResponse schema.
    """
    _validate_extension(file.filename or "unknown")
    _validate_size(file)

    start_ms = time.monotonic()

    # Save the file (even in mock mode we persist it so the upload flow works)
    saved_path = _save_file(file)

    # Determine which mock dataset to return
    doc_type = _guess_doc_type(file.filename or "")
    response = _build_response(doc_type, file.filename or saved_path.name)

    # Overwrite the stored processing_time_ms with the real elapsed time
    elapsed_ms = int((time.monotonic() - start_ms) * 1000)
    response["processing_time_ms"] = elapsed_ms

    return response


def get_demo_analysis(document_type: str) -> dict:
    """
    Return a pre-built mock analysis for one of the three demo document types.
    Raises 404 if document_type is not recognised.
    """
    key = document_type.lower().strip()

    if key not in MOCK_DATA:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Demo document type '{document_type}' not found. "
                f"Available types: {', '.join(SUPPORTED_DEMO_TYPES)}"
            ),
        )

    # Map friendly aliases
    aliases = {
        "employment_agreement": "employment",
        "employment-agreement": "employment",
        "non-disclosure": "nda",
        "non_disclosure": "nda",
        "vendor_agreement": "vendor",
        "vendor-agreement": "vendor",
    }
    key = aliases.get(key, key)

    return _build_response(key, MOCK_DATA[key]["document_name"])
