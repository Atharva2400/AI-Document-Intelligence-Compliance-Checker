"""
mock_analysis.py
----------------
Realistic mock analysis responses for all three demo document types:
  - employment
  - nda
  - vendor

Each entry matches the AnalysisResponse schema exactly so the frontend
receives identical-shaped JSON whether it uploads a real file (Phase 2)
or calls the demo endpoint (Phase 1).
"""

from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")


# ─────────────────────────────────────────────────────────────────────────────
# Employment Agreement
# ─────────────────────────────────────────────────────────────────────────────

EMPLOYMENT_ANALYSIS = {
    "document_name": "Employment_Agreement_v2.pdf",
    "document_type": "Employment Agreement",
    "confidence": 94,
    "tags": ["Employment Law", "Fixed Term", "Indian Jurisdiction", "IT Sector", "Salaried"],

    "extracted_information": [
        {"label": "Employee Name",       "value": "Rahul Sharma",                    "status": "found"},
        {"label": "Company Name",        "value": "TechCorp Solutions Pvt. Ltd.",    "status": "found"},
        {"label": "Role / Designation",  "value": "Senior Software Engineer",        "status": "found"},
        {"label": "Joining Date",        "value": "15 October 2026",                 "status": "found"},
        {"label": "Annual Salary (CTC)", "value": "₹8,00,000",                       "status": "found"},
        {"label": "Notice Period",       "value": "90 Days",                         "status": "found"},
        {"label": "Contract Duration",   "value": "12 Months (Fixed Term)",          "status": "found"},
        {"label": "Probation Period",    "value": "6 Months",                        "status": "found"},
        {"label": "Work Location",       "value": "Bangalore, Karnataka",            "status": "found"},
        {"label": "Governing Law",       "value": "Indian Contract Act, 1872",       "status": "found"},
    ],

    "clauses": [
        {"name": "Salary & Compensation",   "status": "pass",    "clause": "Clause 3",  "detail": "Annual CTC of ₹8,00,000 clearly specified with breakup."},
        {"name": "Confidentiality Agreement","status": "pass",    "clause": "Clause 7",  "detail": "Non-disclosure terms present with 2-year post-employment restriction."},
        {"name": "Termination Clause",      "status": "warning", "clause": "Clause 11", "detail": "Termination period (6 months) contradicts contract duration (12 months)."},
        {"name": "Notice Period",           "status": "pass",    "clause": "Clause 5",  "detail": "90 days notice period specified for both parties."},
        {"name": "Data Protection / PDPA",  "status": "fail",    "clause": "Missing",   "detail": "No data protection or privacy clause found. Required under IT Act 2000."},
        {"name": "Intellectual Property",   "status": "pass",    "clause": "Clause 9",  "detail": "All IP created during employment assigned to employer."},
        {"name": "Non-Compete",             "status": "warning", "clause": "Clause 10", "detail": "Non-compete clause extends to 24 months — may not be enforceable in India."},
        {"name": "Dispute Resolution",      "status": "pass",    "clause": "Clause 14", "detail": "Arbitration under Arbitration and Conciliation Act, 1996."},
        {"name": "Leave Policy",            "status": "pass",    "clause": "Clause 6",  "detail": "18 days annual leave, 12 sick days — complies with Shops Act."},
        {"name": "Probation Terms",         "status": "warning", "clause": "Clause 2",  "detail": "6-month probation with no performance review criteria specified."},
    ],

    "compliance_score": 83,

    "compliance_rules": [
        {
            "id": "CR-001", "rule": "Salary Disclosure", "category": "Financial",
            "status": "pass", "severity": "HIGH",
            "evidence": 'Clause 3: "Annual CTC shall be ₹8,00,000 (Rupees Eight Lakhs only)"',
            "recommendation": "Compliant. No action required.",
        },
        {
            "id": "CR-002", "rule": "Notice Period ≥ 30 Days", "category": "Employment",
            "status": "pass", "severity": "HIGH",
            "evidence": 'Clause 5: "Either party shall give 90 days written notice"',
            "recommendation": "Compliant. Exceeds minimum requirement.",
        },
        {
            "id": "CR-003", "rule": "Contract Duration Consistency", "category": "Structural",
            "status": "fail", "severity": "CRITICAL",
            "evidence": 'Clause 4: "12 months" vs Clause 11: "Employment terminates after 6 months"',
            "recommendation": "Resolve contradiction. Align contract duration across all clauses.",
        },
        {
            "id": "CR-004", "rule": "Data Protection Clause (IT Act 2000)", "category": "Legal Compliance",
            "status": "fail", "severity": "HIGH",
            "evidence": "No data protection or PDPA clause found in document.",
            "recommendation": "Add mandatory data protection clause per IT Act 2000 & DPDPA 2023.",
        },
        {
            "id": "CR-005", "rule": "Dispute Resolution Mechanism", "category": "Legal",
            "status": "pass", "severity": "MEDIUM",
            "evidence": "Clause 14: Arbitration under Arbitration and Conciliation Act, 1996",
            "recommendation": "Compliant. Arbitration clause is enforceable.",
        },
        {
            "id": "CR-006", "rule": "Non-Compete Enforceability (India)", "category": "Restrictive Covenants",
            "status": "warning", "severity": "MEDIUM",
            "evidence": "Clause 10: 24-month non-compete post employment. Indian courts rarely enforce.",
            "recommendation": "Reduce to 6-12 months or add consideration for enforceability.",
        },
        {
            "id": "CR-007", "rule": "Probation Review Criteria", "category": "Employment",
            "status": "warning", "severity": "LOW",
            "evidence": "Clause 2: Probation period defined but no KPIs or review criteria specified.",
            "recommendation": "Add clear performance metrics and review schedule for probation.",
        },
        {
            "id": "CR-008", "rule": "Governing Law Specified", "category": "Legal",
            "status": "pass", "severity": "HIGH",
            "evidence": 'Clause 15: "This Agreement shall be governed by Indian Contract Act, 1872"',
            "recommendation": "Compliant.",
        },
    ],

    "contradictions": [
        {
            "id": "CON-001",
            "title": "Contract Duration vs Termination Period",
            "confidence": 94, "risk": "HIGH", "severity": "CRITICAL",
            "clause1": {
                "id": "Clause 4", "title": "Contract Duration",
                "text": '"The employment shall be for a fixed term of twelve (12) months from the Date of Joining."',
            },
            "clause2": {
                "id": "Clause 11", "title": "Termination",
                "text": '"The employment under this Agreement shall automatically terminate after six (6) months unless renewed in writing."',
            },
            "evidence": "Clause 4 establishes 12-month employment; Clause 11 auto-terminates at 6 months.",
            "impact": "Creates legal ambiguity about employment duration. Employee may have wrongful termination claim.",
            "recommendation": "Align both clauses to the same duration. Consult legal counsel before signing.",
        },
        {
            "id": "CON-002",
            "title": "Notice Period vs Immediate Termination",
            "confidence": 87, "risk": "MEDIUM", "severity": "HIGH",
            "clause1": {
                "id": "Clause 5", "title": "Notice Period",
                "text": '"Either party may terminate by giving ninety (90) days written notice to the other party."',
            },
            "clause2": {
                "id": "Clause 11.3", "title": "Immediate Termination",
                "text": '"The Company reserves the right to terminate employment immediately without notice in case of misconduct."',
            },
            "evidence": "Clause 5 requires 90-day notice; Clause 11.3 allows immediate termination. Overlap not clearly defined.",
            "impact": '"Misconduct" is undefined — gives employer unchecked power to bypass notice period.',
            "recommendation": "Define 'misconduct' explicitly and list specific grounds for immediate termination.",
        },
    ],

    "risk_level": "HIGH",
    "risk_score": 78,
    "total_issues": 7,
    "critical_issues": 1,

    "recommendations": [
        {"priority": 1, "severity": "CRITICAL", "title": "Fix Contract Duration Contradiction",
         "action": "Align Clause 4 and Clause 11 to the same employment duration. Seek legal counsel immediately."},
        {"priority": 2, "severity": "HIGH", "title": "Add Data Protection Clause",
         "action": "Insert DPDPA 2023 compliant data protection and privacy clause before execution."},
        {"priority": 3, "severity": "MEDIUM", "title": "Define Misconduct Scope",
         "action": "List explicit grounds for immediate termination to limit ambiguity in Clause 11.3."},
        {"priority": 4, "severity": "MEDIUM", "title": "Review Non-Compete Duration",
         "action": "Reduce non-compete to 6-12 months or add paid consideration for the restriction period."},
        {"priority": 5, "severity": "LOW", "title": "Add Probation KPIs",
         "action": "Add measurable performance criteria and a formal mid-probation review checkpoint."},
    ],

    "processing_time_ms": 3240,
}


# ─────────────────────────────────────────────────────────────────────────────
# Non-Disclosure Agreement (NDA)
# ─────────────────────────────────────────────────────────────────────────────

NDA_ANALYSIS = {
    "document_name": "NDA_TechCorp_2026.pdf",
    "document_type": "Non-Disclosure Agreement",
    "confidence": 97,
    "tags": ["NDA", "Confidentiality", "Mutual", "Indian Jurisdiction", "B2B"],

    "extracted_information": [
        {"label": "Disclosing Party",      "value": "TechCorp Solutions Pvt. Ltd.",    "status": "found"},
        {"label": "Receiving Party",       "value": "Nexus Innovations Ltd.",           "status": "found"},
        {"label": "Effective Date",        "value": "01 September 2026",               "status": "found"},
        {"label": "Confidentiality Period","value": "3 Years",                          "status": "found"},
        {"label": "Purpose",               "value": "Software product evaluation",      "status": "found"},
        {"label": "Governing Law",         "value": "Indian Contract Act, 1872",        "status": "found"},
        {"label": "Jurisdiction",          "value": "Courts of Bangalore, Karnataka",   "status": "found"},
        {"label": "Exclusions",            "value": "Public domain, prior knowledge",   "status": "found"},
        {"label": "Return of Information", "value": "Within 30 days of termination",    "status": "found"},
        {"label": "Penalty Clause",        "value": "Not specified",                    "status": "missing"},
    ],

    "clauses": [
        {"name": "Definition of Confidential Information", "status": "pass",    "clause": "Clause 1", "detail": "Broad but clear definition including technical, business and financial data."},
        {"name": "Obligations of Receiving Party",         "status": "pass",    "clause": "Clause 3", "detail": "Standard care obligations clearly specified."},
        {"name": "Exclusions from Confidentiality",        "status": "pass",    "clause": "Clause 4", "detail": "Public domain, prior knowledge and legally compelled disclosures properly excluded."},
        {"name": "Term and Duration",                      "status": "warning", "clause": "Clause 6", "detail": "3-year term. No survival clause after expiry — risk of information misuse."},
        {"name": "Return / Destruction of Information",    "status": "pass",    "clause": "Clause 7", "detail": "30-day return requirement upon termination."},
        {"name": "Remedies for Breach",                    "status": "warning", "clause": "Clause 8", "detail": "Injunctive relief mentioned but no liquidated damages or penalty specified."},
        {"name": "Penalty / Liquidated Damages",           "status": "fail",    "clause": "Missing",  "detail": "No financial penalty clause for breach. Weakens enforceability."},
        {"name": "Dispute Resolution",                     "status": "pass",    "clause": "Clause 9", "detail": "Bangalore courts jurisdiction. Arbitration not specified."},
    ],

    "compliance_score": 78,

    "compliance_rules": [
        {
            "id": "CR-001", "rule": "Confidentiality Definition Clarity", "category": "Core NDA",
            "status": "pass", "severity": "HIGH",
            "evidence": "Clause 1 provides comprehensive definition covering technical, business and financial data.",
            "recommendation": "Compliant.",
        },
        {
            "id": "CR-002", "rule": "Survival Clause Post-Expiry", "category": "Duration",
            "status": "fail", "severity": "HIGH",
            "evidence": "No survival clause found. Confidentiality obligations end at 3 years with no extension.",
            "recommendation": "Add survival clause extending key obligations beyond expiry for sensitive IP.",
        },
        {
            "id": "CR-003", "rule": "Liquidated Damages for Breach", "category": "Enforcement",
            "status": "fail", "severity": "HIGH",
            "evidence": "Clause 8 mentions injunctive relief only. No financial penalty for breach.",
            "recommendation": "Add liquidated damages clause with agreed penalty amount to deter breach.",
        },
        {
            "id": "CR-004", "rule": "Permitted Disclosures (Legal Compulsion)", "category": "Exclusions",
            "status": "pass", "severity": "MEDIUM",
            "evidence": "Clause 4.3 covers legally compelled disclosure with notice requirement.",
            "recommendation": "Compliant.",
        },
        {
            "id": "CR-005", "rule": "Data Protection Compliance", "category": "Legal Compliance",
            "status": "warning", "severity": "MEDIUM",
            "evidence": "No explicit reference to DPDPA 2023 for personal data shared under NDA.",
            "recommendation": "Add a DPDPA 2023 data handling clause for any personal data exchanged.",
        },
    ],

    "contradictions": [
        {
            "id": "CON-001",
            "title": "Confidentiality Duration vs No Survival Clause",
            "confidence": 89, "risk": "MEDIUM", "severity": "HIGH",
            "clause1": {
                "id": "Clause 6", "title": "Term",
                "text": '"This Agreement shall remain in force for a period of three (3) years from the Effective Date."',
            },
            "clause2": {
                "id": "Clause 8", "title": "Remedies",
                "text": '"Upon expiry, the obligations of confidentiality shall cease and the Receiving Party shall be relieved of all duties."',
            },
            "evidence": "Clause 6 sets 3-year term; Clause 8 fully releases obligations at expiry — no survival for trade secrets.",
            "impact": "Trade secrets and sensitive IP lose legal protection after 3 years even if they remain confidential.",
            "recommendation": "Add a survival clause: key confidentiality obligations should survive termination indefinitely for trade secrets.",
        },
    ],

    "risk_level": "MEDIUM",
    "risk_score": 58,
    "total_issues": 4,
    "critical_issues": 0,

    "recommendations": [
        {"priority": 1, "severity": "HIGH", "title": "Add Survival Clause",
         "action": "Extend confidentiality obligations beyond expiry for trade secrets and sensitive IP."},
        {"priority": 2, "severity": "HIGH", "title": "Add Liquidated Damages",
         "action": "Specify agreed financial penalty for breach to strengthen enforceability."},
        {"priority": 3, "severity": "MEDIUM", "title": "Reference DPDPA 2023",
         "action": "Add a data protection addendum for personal data exchanged under the NDA."},
        {"priority": 4, "severity": "LOW", "title": "Consider Arbitration Clause",
         "action": "Add arbitration under Arbitration & Conciliation Act, 1996 for faster dispute resolution."},
    ],

    "processing_time_ms": 2180,
}


# ─────────────────────────────────────────────────────────────────────────────
# Vendor Agreement
# ─────────────────────────────────────────────────────────────────────────────

VENDOR_ANALYSIS = {
    "document_name": "Vendor_Agreement_Q3.pdf",
    "document_type": "Vendor / Service Agreement",
    "confidence": 91,
    "tags": ["Vendor", "B2B", "Service Contract", "SLA", "Indian Jurisdiction"],

    "extracted_information": [
        {"label": "Client",              "value": "TechCorp Solutions Pvt. Ltd.",    "status": "found"},
        {"label": "Vendor",              "value": "CloudServe Technologies Ltd.",    "status": "found"},
        {"label": "Services",            "value": "Cloud infrastructure & DevOps",  "status": "found"},
        {"label": "Contract Value",      "value": "₹24,00,000 per annum",           "status": "found"},
        {"label": "Payment Terms",       "value": "Net-30 days",                    "status": "found"},
        {"label": "Contract Start",      "value": "01 October 2026",               "status": "found"},
        {"label": "Contract Duration",   "value": "12 Months (renewable)",          "status": "found"},
        {"label": "SLA Uptime",          "value": "99.5%",                          "status": "found"},
        {"label": "Penalty for SLA Breach","value": "Not specified",               "status": "missing"},
        {"label": "Governing Law",       "value": "Indian Contract Act, 1872",      "status": "found"},
        {"label": "Termination Notice",  "value": "60 Days",                        "status": "found"},
        {"label": "Liability Cap",       "value": "Not specified",                  "status": "missing"},
    ],

    "clauses": [
        {"name": "Scope of Services",        "status": "pass",    "clause": "Clause 2",  "detail": "Services clearly defined with deliverable schedule attached as Exhibit A."},
        {"name": "Payment Terms",            "status": "pass",    "clause": "Clause 4",  "detail": "Net-30 payment terms with late payment interest at 1.5% per month."},
        {"name": "SLA Definition",           "status": "pass",    "clause": "Clause 6",  "detail": "99.5% uptime SLA defined with measurement methodology."},
        {"name": "SLA Penalty / Credit",     "status": "fail",    "clause": "Missing",   "detail": "No penalty or credit mechanism for SLA breach. SLA is unenforceable without remedy."},
        {"name": "Liability Cap",            "status": "fail",    "clause": "Missing",   "detail": "No limitation of liability clause. Vendor has unlimited exposure."},
        {"name": "IP Ownership",             "status": "warning", "clause": "Clause 9",  "detail": "Custom deliverables IP assignment ambiguous — does not clearly state client owns custom work."},
        {"name": "Data Security",            "status": "warning", "clause": "Clause 10", "detail": "General security clause present but no specific standards (ISO 27001, SOC 2) mentioned."},
        {"name": "Termination for Convenience","status": "pass",  "clause": "Clause 12", "detail": "60-day notice termination for convenience by either party."},
        {"name": "Force Majeure",            "status": "pass",    "clause": "Clause 13", "detail": "Standard force majeure clause covering natural disasters and government actions."},
        {"name": "Dispute Resolution",       "status": "pass",    "clause": "Clause 15", "detail": "Two-stage: negotiation then arbitration under Arbitration & Conciliation Act, 1996."},
        {"name": "Confidentiality",          "status": "pass",    "clause": "Clause 11", "detail": "Mutual confidentiality obligations for the term plus 2 years."},
        {"name": "Indemnification",          "status": "warning", "clause": "Clause 14", "detail": "One-sided indemnification — vendor indemnifies client but not vice versa."},
    ],

    "compliance_score": 71,

    "compliance_rules": [
        {
            "id": "CR-001", "rule": "SLA Enforcement Mechanism", "category": "Service Levels",
            "status": "fail", "severity": "HIGH",
            "evidence": "Clause 6 defines 99.5% uptime SLA but no credit or penalty mechanism exists.",
            "recommendation": "Add SLA credit table: e.g., 10% monthly fee credit per 0.5% below SLA threshold.",
        },
        {
            "id": "CR-002", "rule": "Limitation of Liability", "category": "Risk Management",
            "status": "fail", "severity": "CRITICAL",
            "evidence": "No liability cap clause found anywhere in the 18-page document.",
            "recommendation": "Add liability cap (typically 12 months of contract value) with carve-outs for gross negligence.",
        },
        {
            "id": "CR-003", "rule": "IP Ownership of Custom Deliverables", "category": "Intellectual Property",
            "status": "warning", "severity": "HIGH",
            "evidence": 'Clause 9: "Vendor retains all IP" — does not differentiate between pre-existing and custom deliverables.',
            "recommendation": "Explicitly assign ownership of custom-developed deliverables to client using work-for-hire language.",
        },
        {
            "id": "CR-004", "rule": "Data Security Standards Reference", "category": "Security",
            "status": "warning", "severity": "MEDIUM",
            "evidence": "Clause 10 mentions 'reasonable security measures' without specifying applicable standards.",
            "recommendation": "Reference ISO 27001 or SOC 2 Type II and require annual audit reports.",
        },
        {
            "id": "CR-005", "rule": "Payment Terms and Late Fees", "category": "Financial",
            "status": "pass", "severity": "MEDIUM",
            "evidence": "Clause 4: Net-30 with 1.5% per month interest on late payments.",
            "recommendation": "Compliant.",
        },
        {
            "id": "CR-006", "rule": "Dispute Resolution Mechanism", "category": "Legal",
            "status": "pass", "severity": "MEDIUM",
            "evidence": "Clause 15: Two-stage process — negotiation (30 days) then arbitration.",
            "recommendation": "Compliant.",
        },
    ],

    "contradictions": [
        {
            "id": "CON-001",
            "title": "SLA Commitment Without Enforcement Remedy",
            "confidence": 96, "risk": "HIGH", "severity": "CRITICAL",
            "clause1": {
                "id": "Clause 6.1", "title": "SLA Commitment",
                "text": '"Vendor guarantees 99.5% monthly uptime for all covered services."',
            },
            "clause2": {
                "id": "Clause 6.4", "title": "Remedies",
                "text": '"In the event of SLA breach, parties shall discuss remediation in good faith."',
            },
            "evidence": "Clause 6.1 creates a binding SLA; Clause 6.4 provides no enforceable remedy — only vague 'good faith discussion'.",
            "impact": "SLA is legally unenforceable. Client has no financial remedy for downtime.",
            "recommendation": "Replace 'good faith discussion' with a specific credit table tied to breach severity.",
        },
        {
            "id": "CON-002",
            "title": "IP Ownership — Vendor Retains All vs Client Expects Custom IP",
            "confidence": 82, "risk": "HIGH", "severity": "HIGH",
            "clause1": {
                "id": "Clause 9.1", "title": "IP Ownership",
                "text": '"All intellectual property, including custom deliverables, shall remain the sole property of the Vendor."',
            },
            "clause2": {
                "id": "Clause 2.3", "title": "Deliverables",
                "text": '"Vendor shall develop and deliver custom software modules as per client specifications in Exhibit A."',
            },
            "evidence": "Clause 2.3 establishes client-specific custom development; Clause 9.1 assigns all IP to vendor.",
            "impact": "Client pays for custom development but does not own it. Significant commercial and legal risk.",
            "recommendation": "Amend Clause 9.1 to grant client full ownership of all custom deliverables with vendor retaining pre-existing IP only.",
        },
    ],

    "risk_level": "HIGH",
    "risk_score": 82,
    "total_issues": 9,
    "critical_issues": 2,

    "recommendations": [
        {"priority": 1, "severity": "CRITICAL", "title": "Add Liability Cap",
         "action": "Insert limitation of liability clause capped at 12 months contract value with carve-outs for IP infringement and data breach."},
        {"priority": 2, "severity": "CRITICAL", "title": "Add SLA Credit/Penalty Table",
         "action": "Define specific credit percentages for each tier of SLA breach (e.g., >99.5%: no credit, 99-99.5%: 5%, <99%: 15%)."},
        {"priority": 3, "severity": "HIGH", "title": "Fix IP Ownership Clause",
         "action": "Grant client ownership of all custom deliverables. Vendor retains pre-existing IP and grants license to client."},
        {"priority": 4, "severity": "HIGH", "title": "Specify Security Standards",
         "action": "Require ISO 27001 certification or SOC 2 Type II audit report annually."},
        {"priority": 5, "severity": "MEDIUM", "title": "Balance Indemnification",
         "action": "Add mutual indemnification provisions to protect both parties."},
    ],

    "processing_time_ms": 3890,
}


# ─────────────────────────────────────────────────────────────────────────────
# Registry — accessed by document_service.py
# ─────────────────────────────────────────────────────────────────────────────

MOCK_DATA: dict[str, dict] = {
    "employment": EMPLOYMENT_ANALYSIS,
    "nda": NDA_ANALYSIS,
    "vendor": VENDOR_ANALYSIS,
}

SUPPORTED_DEMO_TYPES = list(MOCK_DATA.keys())
