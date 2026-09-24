"""
Pydantic schemas for AI Document Intelligence API.
These define the exact shape of every request and response so the
frontend always receives predictable, type-safe JSON.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Shared building blocks
# ---------------------------------------------------------------------------

class ExtractedField(BaseModel):
    """A single key-value pair pulled out of the document."""
    label: str = Field(..., description="Human-readable field name")
    value: str = Field(..., description="Extracted value")
    status: str = Field(default="found", description="found | missing | uncertain")


class ClauseResult(BaseModel):
    """Analysis result for one contract clause."""
    name: str
    status: str = Field(..., description="pass | warning | fail")
    clause: str = Field(..., description="e.g. 'Clause 3' or 'Missing'")
    detail: str


class ComplianceRule(BaseModel):
    """One compliance rule check with evidence and severity."""
    id: str
    rule: str
    category: str
    status: str = Field(..., description="pass | warning | fail")
    severity: str = Field(..., description="CRITICAL | HIGH | MEDIUM | LOW")
    evidence: str
    recommendation: str


class ClauseRef(BaseModel):
    """Reference to a specific clause inside a document."""
    id: str          # e.g. "Clause 4"
    title: str
    text: str


class Contradiction(BaseModel):
    """An AI-detected contradiction between two clauses."""
    id: str
    title: str
    confidence: int = Field(..., ge=0, le=100)
    risk: str
    severity: str
    clause1: ClauseRef
    clause2: ClauseRef
    evidence: str
    impact: str
    recommendation: str


class Recommendation(BaseModel):
    """A top-level action recommendation."""
    priority: int
    severity: str
    title: str
    action: str


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    message: str = "AI Document Intelligence API is running"


class AnalysisResponse(BaseModel):
    """
    Complete analysis result returned by POST /api/analyze
    and GET /api/demo/{document_type}.
    """
    # ── Document identity ──
    document_name: str
    document_type: str
    confidence: int = Field(..., ge=0, le=100, description="AI classification confidence %")
    tags: List[str] = []

    # ── Extracted content ──
    extracted_information: List[ExtractedField]
    clauses: List[ClauseResult]

    # ── Compliance ──
    compliance_score: int = Field(..., ge=0, le=100)
    compliance_rules: List[ComplianceRule]

    # ── Contradictions ──
    contradictions: List[Contradiction]

    # ── Risk ──
    risk_level: str = Field(..., description="LOW | MEDIUM | HIGH | CRITICAL")
    risk_score: int = Field(..., ge=0, le=100)

    # ── Summary ──
    total_issues: int
    critical_issues: int
    recommendations: List[Recommendation]

    # ── Meta ──
    processing_time_ms: int
    analyzed_at: str


class ErrorResponse(BaseModel):
    """Standard error envelope."""
    error: str
    detail: Optional[str] = None
    status_code: int
