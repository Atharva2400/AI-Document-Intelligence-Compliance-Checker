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
    Converts Gemini output format into the AnalysisResponse JSON structure.
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

    # 2. Clauses
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

    raw_missing = gemini_data.get("missing_clauses") or []
    if isinstance(raw_missing, list):
        for c in raw_missing:
            if isinstance(c, dict):
                clauses.append({
                    "name": str(c.get("name", "Missing Clause")),
                    "status": "fail",
                    "clause": str(c.get("clause", "Missing")),
                    "detail": str(c.get("detail", ""))
                })

    # 3. Compliance Rules (Findings)
    compliance_rules = []
    raw_findings = gemini_data.get("findings") or []
    if isinstance(raw_findings, list):
        for idx, f in enumerate(raw_findings, 1):
            if isinstance(f, dict):
                st = str(f.get("status", "warning")).lower()
                if st not in ["pass", "warning", "fail"]:
                    st = "warning"
                sev = str(f.get("severity", "MEDIUM")).upper()
                if sev not in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                    sev = "MEDIUM"
                compliance_rules.append({
                    "id": str(f.get("id", f"CR-{idx:03d}")),
                    "rule": str(f.get("rule", f.get("name", "Compliance Check"))),
                    "category": str(f.get("category", "General")),
                    "status": st,
                    "severity": sev,
                    "evidence": str(f.get("evidence", "N/A")),
                    "recommendation": str(f.get("recommendation", "Review clause."))
                })

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

    # Metrics
    critical_count = sum(1 for item in compliance_rules + contradictions + recommendations if item.get("severity") == "CRITICAL")
    high_count = sum(1 for item in compliance_rules + contradictions + recommendations if item.get("severity") == "HIGH")
    fail_count = sum(1 for c in clauses if c.get("status") == "fail") + sum(1 for r in compliance_rules if r.get("status") == "fail") + len(contradictions)
    warning_count = sum(1 for c in clauses if c.get("status") == "warning") + sum(1 for r in compliance_rules if r.get("status") == "warning")

    total_issues = len(contradictions) + sum(1 for c in clauses if c.get("status") in ["warning", "fail"]) + sum(1 for r in compliance_rules if r.get("status") in ["warning", "fail"])
    critical_issues = critical_count

    deductions = (critical_count * 20) + (high_count * 10) + (fail_count * 10) + (warning_count * 5)
    compliance_score = max(0, 100 - deductions)
    risk_score = min(100, max(0, 100 - compliance_score))

    if critical_issues > 0 or risk_score >= 75:
        risk_level = "CRITICAL"
    elif high_count > 0 or risk_score >= 50:
        risk_level = "HIGH"
    elif total_issues > 0 or risk_score >= 25:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

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
        "compliance_score": compliance_score,
        "compliance_rules": compliance_rules,
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
    Deep-copy the mock payload, inject real-time metadata, and return it.
    """
    payload = copy.deepcopy(MOCK_DATA[doc_type])
    payload["document_name"] = document_name
    payload["analyzed_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    return payload


# ─────────────────────────────────────────────────────────────────────────────
# Public service functions
# ─────────────────────────────────────────────────────────────────────────────

def analyze_uploaded_document(file: UploadFile) -> dict:
    """
    Full processing pipeline for a user-uploaded document:
      1. Validate extension
      2. Validate size
      3. Save to uploads/
      4. Extract text (PDF, DOCX, TXT)
      5. Send extracted text to Gemini for analysis
      6. Convert Gemini result into AnalysisResponse JSON format
    """
    _validate_extension(file.filename or "unknown")
    _validate_size(file)

    start_ms = time.monotonic()

    saved_path = _save_file(file)
    extracted_text = _extract_text(saved_path)

    try:
        gemini_result = analyze_document_with_gemini(extracted_text)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gemini analysis failed: {str(e)}"
        )

    elapsed_ms = int((time.monotonic() - start_ms) * 1000)
    response = _convert_gemini_to_analysis_response(gemini_result, file.filename or saved_path.name, elapsed_ms)

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
