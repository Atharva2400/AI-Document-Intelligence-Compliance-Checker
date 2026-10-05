"""
document_service.py
-------------------
All business logic lives here — document extraction, Gemini analysis integration,
and formatting for the API responses.
"""

import os
import time
import copy
import shutil
from datetime import datetime
from pathlib import Path

import pypdf
import docx
from fastapi import UploadFile, HTTPException

from data.mock_analysis import MOCK_DATA, SUPPORTED_DEMO_TYPES
from services.gemini_service import analyze_document_with_gemini
from services.compliance_service import evaluate_compliance
from services.storage_service import upload_to_supabase

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
    """Raise 413 if the file is too large."""
    if hasattr(file, "size") and file.size and file.size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024*1024)} MB.",
        )


def _save_file(file: UploadFile) -> Path:
    """
    Temporarily persist the uploaded file to the uploads/ directory.
    Returns the path where it was saved.
    """
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_name = f"{timestamp}_{file.filename}"
    dest = UPLOAD_DIR / safe_name

    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    return dest


def _extract_text(file_path: Path) -> str:
    """
    Extract readable text from PDF, DOCX, or TXT files.
    Raises HTTPException 400 if unreadable or empty.
    """
    ext = file_path.suffix.lower()
    text = ""
    try:
        if ext == ".pdf":
            reader = pypdf.PdfReader(file_path)
            pages_text = []
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    pages_text.append(t)
            text = "\n".join(pages_text)
        elif ext == ".docx":
            doc = docx.Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text]
            text = "\n".join(paragraphs)
        elif ext == ".txt":
            with open(file_path, "rb") as f:
                raw = f.read()
            for enc in ["utf-8", "latin-1", "cp1252"]:
                try:
                    text = raw.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
            if not text:
                text = raw.decode("utf-8", errors="replace")
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error extracting text from file '{file_path.name}': {str(e)}"
        )

    text = text.strip()
    if not text:
        raise HTTPException(
            status_code=400,
            detail=f"The uploaded document '{file_path.name}' appears to be empty or unreadable text could not be extracted."
        )

    return text


def _convert_gemini_to_analysis_response(gemini_data: dict, document_name: str, elapsed_ms: int) -> dict:
    """
    Converts Gemini output format into the AnalysisResponse JSON structure,
    merging the results of the Python Compliance Rule Engine.
    """
    doc_type = gemini_data.get("document_type") or "Document"
    confidence = gemini_data.get("confidence", 85)
    try:
        confidence = min(max(int(confidence), 0), 100)
    except (ValueError, TypeError):
        confidence = 85

    # 1. Extracted Information
    extracted_info_raw = gemini_data.get("extracted_information") or {}
    extracted_information = []
    if isinstance(extracted_info_raw, dict):
        for k, v in extracted_info_raw.items():
            if v is not None:
                v_str = str(v).strip()
                status = "found" if v_str and v_str.lower() not in ["not specified", "missing", "n/a", "none"] else "missing"
                extracted_information.append({
                    "label": str(k),
                    "value": v_str,
                    "status": status
                })
    elif isinstance(extracted_info_raw, list):
        for item in extracted_info_raw:
            if isinstance(item, dict):
                extracted_information.append({
                    "label": str(item.get("label", item.get("name", "Field"))),
                    "value": str(item.get("value", "")),
                    "status": str(item.get("status", "found"))
                })

    # 2. Clauses & Missing Clauses
    clauses = []
    raw_clauses = gemini_data.get("clauses") or []
    if isinstance(raw_clauses, list):
        for c in raw_clauses:
            if isinstance(c, dict):
                st = str(c.get("status", "pass")).lower()
                if st not in ["pass", "warning", "fail"]:
                    st = "pass"
                clauses.append({
                    "name": str(c.get("name", "Clause")),
                    "status": st,
                    "clause": str(c.get("clause", "Clause")),
                    "detail": str(c.get("detail", ""))
                })

    missing_clauses = gemini_data.get("missing_clauses") or []
    if isinstance(missing_clauses, list):
        for c in missing_clauses:
            if isinstance(c, dict):
                clauses.append({
                    "name": str(c.get("name", "Missing Clause")),
                    "status": "fail",
                    "clause": str(c.get("clause", "Missing")),
                    "detail": str(c.get("detail", ""))
                })

    findings = gemini_data.get("findings") or []

    # 3. Python Compliance Rule Engine
    try:
        comp_result = evaluate_compliance(
            document_type=doc_type,
            extracted_information=extracted_information,
            clauses=clauses
        )
        compliance_score = comp_result["compliance_score"]
        compliance_status = comp_result["compliance_status"]
        compliance_rules = comp_result["compliance_rules"]
        compliance_summary = comp_result["summary"]
        comp_total_issues = comp_result["total_issues"]
        comp_critical_issues = comp_result["critical_issues"]
        risk_level = comp_result["risk_level"]
        risk_score = comp_result["risk_score"]
    except Exception as e:
        compliance_score = None
        compliance_status = "UNAVAILABLE"
        compliance_rules = []
        compliance_summary = f"Compliance engine error: {str(e)}"
        comp_total_issues = 0
        comp_critical_issues = 0
        risk_level = "UNKNOWN"
        risk_score = 0

    # 4. Contradictions
    contradictions = []
    raw_contradictions = gemini_data.get("contradictions") or []
    if isinstance(raw_contradictions, list):
        for idx, con in enumerate(raw_contradictions, 1):
            if isinstance(con, dict):
                c1 = con.get("clause1") or {}
                c2 = con.get("clause2") or {}
                conf = con.get("confidence", 85)
                try:
                    conf = min(max(int(conf), 0), 100)
                except (ValueError, TypeError):
                    conf = 85

                risk = str(con.get("risk", "MEDIUM")).upper()
                sev = str(con.get("severity", "HIGH")).upper()

                contradictions.append({
                    "id": str(con.get("id", f"CON-{idx:03d}")),
                    "title": str(con.get("title", "Contradiction Detected")),
                    "confidence": conf,
                    "risk": risk if risk in ["CRITICAL", "HIGH", "MEDIUM", "LOW"] else "MEDIUM",
                    "severity": sev if sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"] else "HIGH",
                    "clause1": {
                        "id": str(c1.get("id", "Clause A")),
                        "title": str(c1.get("title", "First Clause")),
                        "text": str(c1.get("text", ""))
                    },
                    "clause2": {
                        "id": str(c2.get("id", "Clause B")),
                        "title": str(c2.get("title", "Second Clause")),
                        "text": str(c2.get("text", ""))
                    },
                    "evidence": str(con.get("evidence", "")),
                    "impact": str(con.get("impact", "")),
                    "recommendation": str(con.get("recommendation", ""))
                })

    # 5. Recommendations
    recommendations = []
    raw_recs = gemini_data.get("recommendations") or []
    if isinstance(raw_recs, list):
        for idx, r in enumerate(raw_recs, 1):
            if isinstance(r, dict):
                prio = r.get("priority", idx)
                try:
                    prio = int(prio)
                except (ValueError, TypeError):
                    prio = idx
                sev = str(r.get("severity", "MEDIUM")).upper()
                recommendations.append({
                    "priority": prio,
                    "severity": sev if sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"] else "MEDIUM",
                    "title": str(r.get("title", f"Recommendation {idx}")),
                    "action": str(r.get("action", ""))
                })

    # Deterministic Issue Counts
    total_issues = comp_total_issues + len(contradictions)
    critical_issues = comp_critical_issues + sum(1 for c in contradictions if c.get("severity") in ["CRITICAL", "Critical"])

    tags = [doc_type]
    dt_lower = doc_type.lower()
    if "nda" in dt_lower or "non-disclosure" in dt_lower:
        tags.extend(["NDA", "Confidentiality"])
    elif "employment" in dt_lower:
        tags.extend(["Employment Law", "Contract"])
    elif "vendor" in dt_lower or "service" in dt_lower:
        tags.extend(["Vendor", "SLA", "B2B"])
    else:
        tags.extend(["Document Analysis"])

    return {
        "document_name": document_name,
        "document_type": doc_type,
        "confidence": confidence,
        "tags": list(dict.fromkeys(tags)),
        "extracted_information": extracted_information,
        "clauses": clauses,
        "missing_clauses": missing_clauses,
        "findings": findings,
        "compliance_score": compliance_score,
        "compliance_status": compliance_status,
        "compliance_rules": compliance_rules,
        "compliance_summary": compliance_summary,
        "contradictions": contradictions,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "total_issues": total_issues,
        "critical_issues": critical_issues,
        "recommendations": recommendations,
        "processing_time_ms": elapsed_ms,
        "analyzed_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }


def _build_mock_response(doc_type: str, document_name: str) -> dict:
    """
    Deep-copy the mock payload, run Python Compliance Rule Engine, inject real-time metadata, and return it.
    """
    payload = copy.deepcopy(MOCK_DATA[doc_type])
    payload["document_name"] = document_name
    payload["analyzed_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # Evaluate using Python Compliance Rule Engine
    try:
        comp_result = evaluate_compliance(
            document_type=payload.get("document_type", doc_type),
            extracted_information=payload.get("extracted_information", []),
            clauses=payload.get("clauses", [])
        )
        payload["compliance_score"] = comp_result["compliance_score"]
        payload["compliance_status"] = comp_result["compliance_status"]
        payload["compliance_rules"] = comp_result["compliance_rules"]
        payload["compliance_summary"] = comp_result["summary"]
        payload["total_issues"] = comp_result["total_issues"]
        payload["critical_issues"] = comp_result["critical_issues"]
        payload["risk_level"] = comp_result["risk_level"]
        payload["risk_score"] = comp_result["risk_score"]
    except Exception as e:
        payload["compliance_score"] = None
        payload["compliance_status"] = "UNAVAILABLE"
        payload["compliance_summary"] = f"Compliance engine error: {str(e)}"

    return payload


# ─────────────────────────────────────────────────────────────────────────────
# Public service functions
# ─────────────────────────────────────────────────────────────────────────────

def analyze_uploaded_document(file: UploadFile) -> dict:
    """
    Full processing pipeline for a user-uploaded document:
      1. Validate extension & size
      2. Save to local uploads/
      3. Upload original to Supabase Storage (if SUPABASE_ENABLED=true, non-blocking)
      4. Extract text (PDF, DOCX, TXT)
      5. Send extracted text to Gemini for analysis
      6. Convert Gemini result + evaluate Python Compliance Engine
      7. Return combined response (with optional storage metadata)
    """
    _validate_extension(file.filename or "unknown")
    _validate_size(file)

    start_ms = time.monotonic()

    # Step 2 — save locally (existing behaviour, unchanged)
    saved_path = _save_file(file)

    # Step 3 — upload original to Supabase (non-blocking; never crashes the pipeline)
    unique_filename = saved_path.name        # e.g. "20261005_123456_employee_bond.pdf"
    storage_meta = upload_to_supabase(saved_path, unique_filename)

    # Step 4 — extract text (existing behaviour, unchanged)
    extracted_text = _extract_text(saved_path)

    # Step 5 — Gemini analysis (existing behaviour, unchanged)
    try:
        gemini_result = analyze_document_with_gemini(extracted_text)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gemini analysis failed: {str(e)}"
        )

    elapsed_ms = int((time.monotonic() - start_ms) * 1000)

    # Step 6 — convert + compliance engine (existing behaviour, unchanged)
    response = _convert_gemini_to_analysis_response(gemini_result, file.filename or saved_path.name, elapsed_ms)

    # Step 7 — attach optional storage metadata (additive only, does not rename/remove existing fields)
    response["storage"] = storage_meta

    return response


def get_demo_analysis(document_type: str) -> dict:
    """
    Return a pre-built mock analysis for one of the three demo document types.
    Raises 404 if document_type is not recognised.
    """
    key = document_type.lower().strip()

    if key not in MOCK_DATA:
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

    if key not in MOCK_DATA:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Demo document type '{document_type}' not found. "
                f"Available types: {', '.join(SUPPORTED_DEMO_TYPES)}"
            ),
        )

    return _build_mock_response(key, MOCK_DATA[key]["document_name"])
