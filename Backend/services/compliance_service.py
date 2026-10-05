"""
compliance_service.py
---------------------
Custom Python Compliance Rule Engine for AI Document Intelligence.

Performs 100% deterministic rule evaluation, scoring, risk calculation,
and issue counting based on document-extracted facts and clauses.
Does NOT rely on Gemini for compliance scores, risk levels, or issue counts.
"""

import logging
from typing import Any, Dict, List, Tuple

# ---------------------------------------------------------------------------
# Backend Logger Setup
# ---------------------------------------------------------------------------

logger = logging.getLogger("compliance_engine")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [ComplianceEngine] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


# ---------------------------------------------------------------------------
# Deterministic Penalty Map (Requirement 7)
# ---------------------------------------------------------------------------
# START SCORE = 100
# FAIL:
#   Critical = -15
#   High = -10
#   Medium = -7
#   Low = -3
# WARNING:
#   Critical = -8
#   High = -5
#   Medium = -3
#   Low = -1
# PASS: 0

PENALTY_MAP: Dict[Tuple[str, str], int] = {
    ("FAIL", "Critical"): 15,
    ("FAIL", "High"): 10,
    ("FAIL", "Medium"): 7,
    ("FAIL", "Low"): 3,
    ("WARNING", "Critical"): 8,
    ("WARNING", "High"): 5,
    ("WARNING", "Medium"): 3,
    ("WARNING", "Low"): 1,
    ("PASS", "Critical"): 0,
    ("PASS", "High"): 0,
    ("PASS", "Medium"): 0,
    ("PASS", "Low"): 0,
}


def _get_extracted_dict(extracted_info: Any) -> Dict[str, str]:
    """
    Normalizes extracted_information into a dictionary of {lowercased_key: raw_value}.
    """
    info_dict: Dict[str, str] = {}

    if isinstance(extracted_info, dict):
        for k, v in extracted_info.items():
            if v is not None:
                val_str = str(v).strip()
                norm_key = str(k).strip().lower()
                info_dict[norm_key] = val_str
    elif isinstance(extracted_info, list):
        for item in extracted_info:
            if isinstance(item, dict):
                lbl = str(item.get("label", item.get("name", item.get("rule", "")))).strip()
                val = str(item.get("value", "")).strip()
                if lbl:
                    info_dict[lbl.lower()] = val

    return info_dict


def _normalize_clauses(clauses_input: Any) -> List[Dict[str, str]]:
    """
    Normalizes clauses list into standard format with name, status, clause, detail.
    """
    normalized: List[Dict[str, str]] = []
    if isinstance(clauses_input, list):
        for c in clauses_input:
            if isinstance(c, dict):
                normalized.append({
                    "name": str(c.get("name", c.get("rule", "Clause"))),
                    "status": str(c.get("status", "pass")).lower(),
                    "clause": str(c.get("clause", c.get("id", "Clause"))),
                    "detail": str(c.get("detail", c.get("evidence", c.get("recommendation", ""))))
                })
    return normalized


def _check_field_or_clause(
    keywords: List[str],
    info_dict: Dict[str, str],
    clauses: List[Dict[str, str]],
    field_name: str,
    default_if_missing: Tuple[str, str, str, str] = None
) -> Tuple[str, str, str, str]:
    """
    Evaluates presence and quality of information across both extracted fields and document clauses.
    Returns: (status, evidence, explanation, recommendation)
    """
    # 1. Search extracted_information
    matched_key = None
    matched_val = None
    for kw in keywords:
        for k, v in info_dict.items():
            if kw in k:
                matched_key = k
                matched_val = v
                break
        if matched_key:
            break

    if matched_val and matched_val.strip():
        val_clean = matched_val.strip()
        val_lower = val_clean.lower()

        missing_placeholders = ["missing", "n/a", "none", "not specified", "unknown", "not mentioned", "null"]
        if val_lower not in missing_placeholders:
            ambiguous_terms = ["tbd", "to be decided", "subject to", "unclear", "ambiguous", "pending", "varies", "contradict"]
            if any(term in val_lower for term in ambiguous_terms):
                return (
                    "WARNING",
                    f"Extracted field '{matched_key}' found: '{val_clean}'",
                    f"Field '{matched_key}' is ambiguous, conditional, or subject to dispute.",
                    f"Review agreement and explicitly clarify terms for {field_name.lower()}."
                )
            else:
                return (
                    "PASS",
                    f"Extracted field '{matched_key}' found: '{val_clean}'",
                    f"{field_name} is clearly defined in extracted document fields.",
                    f"Compliant. {field_name} is clearly defined."
                )

    # 2. Search clauses (do not mark FAIL if information is clearly present inside extracted clauses)
    for c in clauses:
        c_name_lower = c["name"].lower()
        c_detail_lower = c["detail"].lower()

        if any(kw in c_name_lower for kw in keywords) or any(kw in c_detail_lower for kw in keywords):
            st = c["status"]
            clause_ref = c["clause"] if c["clause"] and c["clause"] != "Missing" else c["name"]
            detail = c["detail"]

            if st in ["pass", "found"]:
                return (
                    "PASS",
                    f"Clause '{clause_ref}' ({c['name']}): '{detail}'",
                    f"Clause '{c['name']}' addresses {field_name.lower()} satisfactorily.",
                    f"Compliant. {field_name} is covered under {c['name']}."
                )
            elif st == "warning":
                return (
                    "WARNING",
                    f"Clause '{clause_ref}' ({c['name']}) identified with potential issue: '{detail}'",
                    f"Clause '{c['name']}' contains potential ambiguity or inconsistency.",
                    f"Review clause '{c['name']}' to resolve ambiguity or compliance risk."
                )
            elif st == "fail":
                return (
                    "FAIL",
                    f"Clause check for '{c['name']}' indicated failure: '{detail}'",
                    f"Clause '{c['name']}' failed standard compliance checks.",
                    f"Rectify and add explicit terms for {field_name.lower()}."
                )

    # 3. Handle default if missing (e.g. optional exit penalty rules vs mandatory rules)
    if default_if_missing:
        return default_if_missing

    # 4. Missing in both extracted fields and clauses
    return (
        "FAIL",
        f"No clear {field_name.lower()} was identified in extracted fields or document clauses.",
        f"The required provision for {field_name.lower()} is missing from the document.",
        f"Review the agreement and add or clarify {field_name.lower()}."
    )


# ---------------------------------------------------------------------------
# Employment Agreement & Employee Bond Rules (Requirement 4)
# ---------------------------------------------------------------------------

def evaluate_employment_rules(extracted_information: Any, clauses: Any) -> List[Dict[str, Any]]:
    info_dict = _get_extracted_dict(extracted_information)
    norm_clauses = _normalize_clauses(clauses)

    rule_definitions = [
        (
            "EMP-001", "Mandatory Service Commitment",
            "Minimum service commitment period or bond lock-in duration must be specified.",
            "High", "Service Commitment",
            ["service commitment", "bond duration", "minimum service", "service period", "bond period", "lock-in", "contract duration"]
        ),
        (
            "EMP-002", "Training / Recovery Amount",
            "Financial obligation, training recovery cost, or bond amount for early departure must be specified.",
            "High", "Financial Obligation",
            ["training amount", "recovery amount", "bond amount", "training cost", "reimbursement amount", "financial obligation", "salary"]
        ),
        (
            "EMP-003", "Additional Exit Penalty",
            "Any additional liquidated damages or exit penalties must be clearly defined and reasonable.",
            "Critical", "Exit Terms",
            ["exit penalty", "liquidated damages", "additional penalty", "penalty clause", "forfeiture"],
            ("PASS", "No excessive or additional exit penalty identified.", "No additional exit penalty or liquidated damages clause found.", "Compliant. No penalty clause.")
        ),
        (
            "EMP-004", "Salary Deduction Terms",
            "Terms regarding salary deductions or clawbacks must comply with employment norms.",
            "Medium", "Compensation",
            ["salary deduction", "clawback", "deduction from salary", "wage deduction", "payroll deduction"],
            ("PASS", "No unauthorized salary deduction terms specified.", "Standard salary and compensation terms present without unlawful deduction clauses.", "Compliant.")
        ),
        (
            "EMP-005", "Notice Period",
            "Required notice period for resignation or termination must be clearly defined.",
            "High", "Termination",
            ["notice period", "resignation notice", "termination notice"]
        ),
        (
            "EMP-006", "Termination Clause",
            "Clear grounds and conditions for contract termination must be included.",
            "High", "Termination",
            ["termination clause", "termination grounds", "termination conditions", "end of employment"]
        ),
        (
            "EMP-007", "Confidentiality Obligations",
            "Non-disclosure and confidentiality obligations must be clearly stated.",
            "Medium", "Confidentiality",
            ["confidentiality", "non-disclosure", "confidential information", "proprietary data"]
        ),
        (
            "EMP-008", "Data Protection & Privacy",
            "Data protection or employee privacy clause must be included.",
            "Medium", "Data Privacy",
            ["data protection", "privacy policy", "pdpa", "gdpr", "data privacy", "privacy"]
        ),
        (
            "EMP-009", "Contract Duration & Term",
            "Overall contract duration, probation, or employment term must be specified.",
            "Medium", "Timeline",
            ["contract duration", "joining date", "start date", "term", "probation"]
        ),
        (
            "EMP-010", "Employee & Employer Information",
            "Names of employee and employer/company must be clearly stated.",
            "Low", "Parties Identification",
            ["employee name", "company name", "employer name", "parties", "employee", "employer"]
        ),
    ]

    rules: List[Dict[str, Any]] = []
    for item in rule_definitions:
        r_id, r_name, r_desc, r_sev, r_cat, keywords = item[0], item[1], item[2], item[3], item[4], item[5]
        default_missing = item[6] if len(item) > 6 else None

        status, evidence, explanation, recommendation = _check_field_or_clause(
            keywords, info_dict, norm_clauses, r_name, default_if_missing=default_missing
        )

        rules.append({
            "rule_id": r_id,
            "id": r_id,
            "rule_name": r_name,
            "rule": r_name,
            "description": r_desc,
            "explanation": explanation,
            "detail": explanation,
            "category": r_cat,
            "status": status,
            "severity": r_sev,
            "evidence": evidence,
            "recommendation": recommendation,
        })

    return rules


# ---------------------------------------------------------------------------
# Non-Disclosure Agreement Rules
# ---------------------------------------------------------------------------

def evaluate_nda_rules(extracted_information: Any, clauses: Any) -> List[Dict[str, Any]]:
    info_dict = _get_extracted_dict(extracted_information)
    norm_clauses = _normalize_clauses(clauses)

    rule_definitions = [
        ("NDA-001", "Parties Identification", "Disclosing and receiving parties must be clearly identified.", "Low", "Parties", ["disclosing party", "receiving party", "parties", "discloser", "recipient"]),
        ("NDA-002", "Confidential Information Definition", "Scope and definition of confidential information must be clearly defined.", "High", "Core NDA", ["definition of confidential information", "confidential information definition", "confidential information"]),
        ("NDA-003", "Confidentiality Obligations", "Duty of care and non-disclosure obligations must be stated.", "High", "Obligations", ["obligations of receiving party", "confidentiality obligation", "non-disclosure duty", "duty of confidentiality"]),
        ("NDA-004", "Permitted Disclosures / Exceptions", "Exclusions such as public domain knowledge or legal compulsion must be specified.", "Medium", "Exclusions", ["exclusions from confidentiality", "permitted disclosure", "exceptions", "public domain"]),
        ("NDA-005", "Confidentiality Duration", "Duration of confidentiality obligations should be explicitly defined.", "Medium", "Duration", ["confidentiality period", "term and duration", "duration", "term"]),
        ("NDA-006", "Termination / Expiry", "Terms for agreement termination or natural expiry must be present.", "Medium", "Termination", ["termination", "expiry", "expiration"]),
        ("NDA-007", "Return / Deletion of Information", "Obligation to return or destroy confidential data upon termination must be included.", "High", "Information Handling", ["return / destruction of information", "return of information", "deletion of confidential information", "destruction of materials"]),
        ("NDA-008", "Governing Law / Jurisdiction", "Governing law and jurisdiction for legal disputes should be specified when applicable.", "Medium", "Legal", ["governing law", "jurisdiction", "dispute resolution"]),
    ]

    rules: List[Dict[str, Any]] = []
    for r_id, r_name, r_desc, r_sev, r_cat, keywords in rule_definitions:
        status, evidence, explanation, recommendation = _check_field_or_clause(keywords, info_dict, norm_clauses, r_name)
        rules.append({
            "rule_id": r_id,
            "id": r_id,
            "rule_name": r_name,
            "rule": r_name,
            "description": r_desc,
            "explanation": explanation,
            "detail": explanation,
            "category": r_cat,
            "status": status,
            "severity": r_sev,
            "evidence": evidence,
            "recommendation": recommendation,
        })

    return rules


# ---------------------------------------------------------------------------
# Vendor Agreement Rules
# ---------------------------------------------------------------------------

def evaluate_vendor_rules(extracted_information: Any, clauses: Any) -> List[Dict[str, Any]]:
    info_dict = _get_extracted_dict(extracted_information)
    norm_clauses = _normalize_clauses(clauses)

    rule_definitions = [
        ("VND-001", "Vendor / Service Provider", "Vendor or service provider company name must be identified.", "Low", "Parties", ["vendor", "service provider", "contractor", "supplier"]),
        ("VND-002", "Customer / Client Name", "Customer or client organization name must be identified.", "Low", "Parties", ["client", "customer", "company"]),
        ("VND-003", "Scope of Services", "Scope of services, deliverables, and service requirements must be defined.", "High", "Services", ["scope of services", "services", "deliverables", "statement of work"]),
        ("VND-004", "Payment Terms", "Payment schedule, rates, and invoicing terms must be specified.", "High", "Financial", ["payment terms", "contract value", "pricing", "fees", "invoicing"]),
        ("VND-005", "Contract Duration", "Start date, end date, or contract term duration must be stated.", "Medium", "Term", ["contract duration", "contract start", "term", "duration", "effective date"]),
        ("VND-006", "Termination Clause", "Rights and notice periods for contract termination must be included.", "High", "Termination", ["termination notice", "termination for convenience", "termination", "cancellation"]),
        ("VND-007", "Confidentiality Clause", "Confidentiality terms protecting proprietary business data must be present.", "Medium", "Confidentiality", ["confidentiality", "non-disclosure"]),
        ("VND-008", "Liability / Indemnity Clause", "Limitation of liability and indemnification terms should be specified when applicable.", "Critical", "Risk Management", ["liability cap", "limitation of liability", "indemnification", "indemnity", "liability"]),
        ("VND-009", "Data Protection / Security", "Data security, privacy, and protection standards should be included when applicable.", "Medium", "Security & Privacy", ["data security", "data protection", "sla uptime", "security standards", "privacy"]),
        ("VND-010", "Governing Law / Jurisdiction", "Applicable governing law and dispute resolution mechanisms should be specified when applicable.", "Medium", "Legal", ["governing law", "jurisdiction", "dispute resolution"]),
    ]

    rules: List[Dict[str, Any]] = []
    for r_id, r_name, r_desc, r_sev, r_cat, keywords in rule_definitions:
        status, evidence, explanation, recommendation = _check_field_or_clause(keywords, info_dict, norm_clauses, r_name)
        rules.append({
            "rule_id": r_id,
            "id": r_id,
            "rule_name": r_name,
            "rule": r_name,
            "description": r_desc,
            "explanation": explanation,
            "detail": explanation,
            "category": r_cat,
            "status": status,
            "severity": r_sev,
            "evidence": evidence,
            "recommendation": recommendation,
        })

    return rules


# ---------------------------------------------------------------------------
# Master Compliance Evaluator & Deterministic Calculator
# ---------------------------------------------------------------------------

def evaluate_compliance(
    document_type: str,
    extracted_information: Any,
    clauses: Any
) -> Dict[str, Any]:
    """
    Main entry point for the Compliance Rule Engine.

    Calculates deterministically:
      - compliance_score (START=100 minus penalties)
      - total_issues (count of FAIL & WARNING rules + contradictions)
      - critical_issues (count of Critical FAIL & WARNING rules)
      - risk_score (100 - compliance_score)
      - risk_level (highest severity among failing/warning rules: Critical -> HIGH -> MEDIUM -> LOW)

    Returns dictionary with all metrics and rules.
    """
    dt_clean = (document_type or "").lower().strip()

    if "employment" in dt_clean or "employee" in dt_clean or "bond" in dt_clean:
        rules = evaluate_employment_rules(extracted_information, clauses)
    elif "nda" in dt_clean or "non-disclosure" in dt_clean or "confidentiality" in dt_clean:
        rules = evaluate_nda_rules(extracted_information, clauses)
    elif "vendor" in dt_clean or "service" in dt_clean or "supplier" in dt_clean or "contractor" in dt_clean:
        rules = evaluate_vendor_rules(extracted_information, clauses)
    else:
        # Fallback to employment rules for unknown types
        rules = evaluate_employment_rules(extracted_information, clauses)

    logger.info(f"=== Starting Compliance Evaluation for Document Type: '{document_type}' ===")

    # 1. Deterministic Score Calculation (Requirement 7)
    total_penalties = 0
    for r in rules:
        status = r["status"]
        severity = r["severity"]
        penalty = PENALTY_MAP.get((status, severity), 0)
        total_penalties += penalty
        logger.info(f"Rule [{r['rule_id']}] ({r['rule_name']}): status={status}, severity={severity}, penalty=-{penalty}")

    compliance_score = max(0, 100 - total_penalties)

    # 2. Overall Compliance Status
    if compliance_score >= 90:
        compliance_status = "PASS"
    elif compliance_score >= 70:
        compliance_status = "WARNING"
    else:
        compliance_status = "FAIL"

    # 3. Deterministic Issue Counting (Requirement 8 & 9)
    issue_rules = [r for r in rules if r["status"] in ["FAIL", "WARNING"]]
    total_issues = len(issue_rules)

    critical_rules = [r for r in issue_rules if r["severity"].upper() == "CRITICAL"]
    critical_issues = len(critical_rules)

    # 4. Deterministic Risk Level & Risk Score (Requirement 10)
    risk_score = min(100, max(0, 100 - compliance_score))

    severities_present = [r["severity"].upper() for r in issue_rules]

    if "CRITICAL" in severities_present or risk_score >= 75:
        risk_level = "CRITICAL"
    elif "HIGH" in severities_present or risk_score >= 50:
        risk_level = "HIGH"
    elif "MEDIUM" in severities_present or risk_score >= 25:
        risk_level = "MEDIUM"
    elif total_issues > 0:
        risk_level = "LOW"
    else:
        risk_level = "LOW"

    # 5. Short Deterministic Summary
    warn_count = sum(1 for r in rules if r["status"] == "WARNING")
    fail_count = sum(1 for r in rules if r["status"] == "FAIL")

    if compliance_status == "PASS":
        if warn_count == 0 and fail_count == 0:
            summary = "Document passed all compliance checks with no issues identified."
        else:
            summary = "Document passed most compliance checks with a few warnings."
    elif compliance_status == "WARNING":
        if fail_count > 0:
            summary = "Document passed some compliance checks but contains missing or non-compliant elements."
        else:
            summary = "Document passed basic checks but contains several warning conditions."
    else:
        summary = "Document contains several missing or potentially problematic compliance elements."

    logger.info(f"=== Final Evaluation Summary ===")
    logger.info(f"Document Type: {document_type}")
    logger.info(f"Final Compliance Score: {compliance_score}/100 (Total Penalties: -{total_penalties})")
    logger.info(f"Final Compliance Status: {compliance_status}")
    logger.info(f"Total Issues: {total_issues}")
    logger.info(f"Critical Issues: {critical_issues}")
    logger.info(f"Final Risk Score: {risk_score}/100")
    logger.info(f"Final Risk Level: {risk_level}")

    return {
        "compliance_score": compliance_score,
        "compliance_status": compliance_status,
        "compliance_rules": rules,
        "summary": summary,
        "compliance_summary": summary,
        "total_issues": total_issues,
        "critical_issues": critical_issues,
        "risk_level": risk_level,
        "risk_score": risk_score,
    }
