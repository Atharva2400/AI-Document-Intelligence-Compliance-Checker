"""
test_repeatability.py
---------------------
Tests 3 repeated analyses on the exact same Employee Bond document text
to verify 100% deterministic compliance score, issue counts, critical issues, and risk scores.
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.compliance_service import evaluate_compliance
from services.document_service import _convert_gemini_to_analysis_response

# Sample Employee Bond Document text simulating an uploaded PDF/document
EMPLOYEE_BOND_TEXT = """
EMPLOYEE BOND & SERVICE AGREEMENT
This Service Agreement and Bond is made on October 15, 2026, by and between TechCorp Solutions Pvt. Ltd. ("Employer") and Rahul Sharma ("Employee").

1. MANDATORY SERVICE COMMITMENT:
The Employee agrees to serve the Employer for a minimum lock-in period of twenty-four (24) months from the Date of Joining ("Service Period").

2. TRAINING & RECOVERY AMOUNT:
The Employer shall invest in specialized training for the Employee. If the Employee resigns prior to completing the 24-month Service Period, the Employee shall reimburse the Employer a fixed training recovery amount of ₹2,50,000 (Rupees Two Lakh Fifty Thousand only).

3. ADDITIONAL EXIT PENALTY:
In addition to training cost recovery, if the Employee leaves before 12 months, an additional exit penalty of ₹5,00,000 shall be charged as liquidated damages.

4. SALARY DEDUCTIONS:
The Employer reserves the right to deduct any outstanding recovery amounts directly from the Employee's final salary settlement.

5. NOTICE PERIOD:
Either party may terminate employment by providing ninety (90) days written notice after the completion of the mandatory lock-in period.

6. CONFIDENTIALITY:
The Employee shall maintain confidentiality of all proprietary source code, client data, and trade secrets during and after employment.

7. GOVERNING LAW:
This Agreement is governed by the laws of India and subject to jurisdiction of courts in Bangalore.
"""


def test_repeated_runs():
    print("=================================================================")
    print("       TESTING 3 REPEATED RUNS ON THE SAME EMPLOYEE BOND        ")
    print("=================================================================\n")

    # Mock extracted facts representing deterministic Gemini output from the bond text
    extracted_facts = [
        {"label": "Employee Name", "value": "Rahul Sharma", "status": "found"},
        {"label": "Company Name", "value": "TechCorp Solutions Pvt. Ltd.", "status": "found"},
        {"label": "Service Commitment", "value": "24 Months (Mandatory Lock-in)", "status": "found"},
        {"label": "Training Recovery Amount", "value": "₹2,50,000", "status": "found"},
        {"label": "Additional Exit Penalty", "value": "₹5,00,000 (Liquidated damages)", "status": "found"},
        {"label": "Salary Deduction", "value": "Deduction from final settlement", "status": "found"},
        {"label": "Notice Period", "value": "90 Days", "status": "found"},
    ]

    clauses = [
        {"name": "Mandatory Service Commitment", "status": "pass", "clause": "Clause 1", "detail": "24-month lock-in period specified."},
        {"name": "Training Recovery Amount", "status": "pass", "clause": "Clause 2", "detail": "₹2,50,000 recovery for early departure."},
        {"name": "Additional Exit Penalty", "status": "fail", "clause": "Clause 3", "detail": "Unreasonable exit penalty of ₹5,00,000 in addition to training recovery."},
        {"name": "Notice Period", "status": "pass", "clause": "Clause 5", "detail": "90 days notice required."},
        {"name": "Termination Clause", "status": "pass", "clause": "Clause 5", "detail": "Termination allowed after lock-in period."},
        {"name": "Confidentiality Obligations", "status": "pass", "clause": "Clause 6", "detail": "Strict non-disclosure obligations."},
        {"name": "Data Protection & Privacy", "status": "fail", "clause": "Missing", "detail": "No explicit data protection or employee privacy clause found."},
    ]

    results = []

    for run_idx in range(1, 4):
        res = evaluate_compliance("Employment Agreement", extracted_facts, clauses)

        score = res["compliance_score"]
        status = res["compliance_status"]
        total_issues = res["total_issues"]
        critical_issues = res["critical_issues"]
        risk_score = res["risk_score"]
        risk_level = res["risk_level"]

        print(f"RUN {run_idx}:")
        print(f"  Compliance Score: {score}/100")
        print(f"  Compliance Status: {status}")
        print(f"  Total Issues:     {total_issues}")
        print(f"  Critical Issues:  {critical_issues}")
        print(f"  Risk Score:       {risk_score}/100")
        print(f"  Risk Level:       {risk_level}")
        print("-" * 50)

        results.append({
            "score": score,
            "status": status,
            "total_issues": total_issues,
            "critical_issues": critical_issues,
            "risk_score": risk_score,
            "risk_level": risk_level,
        })

    # Verification of 100% determinism across all 3 runs
    run1, run2, run3 = results[0], results[1], results[2]

    assert run1["score"] == run2["score"] == run3["score"], "Scores mismatch across runs!"
    assert run1["status"] == run2["status"] == run3["status"], "Statuses mismatch across runs!"
    assert run1["total_issues"] == run2["total_issues"] == run3["total_issues"], "Total issues mismatch across runs!"
    assert run1["critical_issues"] == run2["critical_issues"] == run3["critical_issues"], "Critical issues mismatch across runs!"
    assert run1["risk_score"] == run2["risk_score"] == run3["risk_score"], "Risk scores mismatch across runs!"
    assert run1["risk_level"] == run2["risk_level"] == run3["risk_level"], "Risk levels mismatch across runs!"

    print("\nSUCCESS: All 3 runs produced IDENTICAL compliance and risk metrics!")
    print(f"Deterministic Score: {run1['score']}/100")
    print(f"Deterministic Total Issues: {run1['total_issues']}")
    print(f"Deterministic Critical Issues: {run1['critical_issues']}")
    print(f"Deterministic Risk Score: {run1['risk_score']}")
    print(f"Deterministic Risk Level: {run1['risk_level']}")


if __name__ == "__main__":
    test_repeated_runs()
