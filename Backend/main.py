"""
main.py
-------
AI Document Intelligence — FastAPI entry point.

Routes
------
GET  /api/health                  → server health check
POST /api/analyze                 → upload & analyze a document
GET  /api/demo/{document_type}    → pre-built mock analysis for employment | nda | vendor

Run
---
  uvicorn main:app --reload --host 127.0.0.1 --port 8000

Interactive docs
---
  http://127.0.0.1:8000/docs      (Swagger UI)
  http://127.0.0.1:8000/redoc     (ReDoc)
"""

import os
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from models.schemas import HealthResponse, AnalysisResponse, ErrorResponse
from services.document_service import (
    analyze_uploaded_document,
    get_demo_analysis,
    SUPPORTED_DEMO_TYPES,
)

# ─────────────────────────────────────────────────────────────────────────────
# Load environment variables from .env (if it exists)
# ─────────────────────────────────────────────────────────────────────────────

load_dotenv()

ALLOWED_ORIGINS: list[str] = [
    o.strip()
    for o in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if o.strip()
]

# ─────────────────────────────────────────────────────────────────────────────
# App
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="AI Document Intelligence API",
    description=(
        "Backend for the AI Document Intelligence & Compliance Checker.\n\n"
        "**Phase 1** — mock analysis only.\n"
        "**Phase 2** — will connect to Google Cloud Storage + Vertex AI + Compliance Engine."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─────────────────────────────────────────────────────────────────────────────
# CORS — allow the React dev server (and any production origin you add later)
# ─────────────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────────────────────
# Global exception handler — returns a clean JSON error envelope
# ─────────────────────────────────────────────────────────────────────────────

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            status_code=exc.status_code,
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),
            status_code=500,
        ).model_dump(),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@app.get(
    "/api/health",
    response_model=HealthResponse,
    summary="Health check",
    tags=["System"],
)
async def health_check():
    """
    Returns `{"status": "ok"}` when the server is running.
    Use this to confirm the backend is reachable from the frontend.
    """
    return HealthResponse()


@app.post(
    "/api/analyze",
    response_model=AnalysisResponse,
    summary="Upload and analyze a document",
    tags=["Analysis"],
)
async def analyze_document(
    file: UploadFile = File(..., description="PDF, DOCX or TXT file to analyze"),
):
    """
    **Upload a document and receive a full compliance analysis.**

    Steps performed (Phase 1 = mock):
    1. Validate file type (PDF / DOCX / TXT) and size (≤ 50 MB)
    2. Save temporarily to `uploads/`
    3. Detect document type from filename
    4. Return realistic mock analysis data

    **Phase 2** will replace step 3-4 with:
    - Google Cloud Storage upload
    - Vertex AI / Gemini document classification & extraction
    - Compliance & Risk Engine evaluation
    """
    result = analyze_uploaded_document(file)
    return result


@app.get(
    "/api/demo/{document_type}",
    response_model=AnalysisResponse,
    summary="Get mock analysis for a demo document",
    tags=["Analysis"],
)
async def demo_analysis(
    document_type: str,
):
    """
    **Returns pre-built analysis without requiring a file upload.**

    Supported `document_type` values:
    - `employment` — Employment Agreement
    - `nda` — Non-Disclosure Agreement
    - `vendor` — Vendor / Service Agreement

    Useful for frontend demos, testing the UI, and integration testing.
    """
    result = get_demo_analysis(document_type)
    return result


@app.get(
    "/api/demo-types",
    summary="List available demo document types",
    tags=["Analysis"],
)
async def list_demo_types():
    """Returns the list of document types supported by GET /api/demo/{document_type}."""
    return {
        "demo_types": SUPPORTED_DEMO_TYPES,
        "description": {
            "employment": "Employment Agreement (Indian jurisdiction, fixed-term)",
            "nda": "Non-Disclosure Agreement (mutual, B2B)",
            "vendor": "Vendor / Service Agreement (cloud infrastructure)",
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# Dev entry point  (python main.py)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=True)
