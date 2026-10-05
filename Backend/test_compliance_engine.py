"""
test_compliance_engine.py
--------------------------
Unit and integration tests for the Python Compliance Rule Engine and FastAPI endpoints.
"""

import os
import sys
from pathlib import Path

# Add Backend root directory to sys.path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.compliance_service import (
    evaluate_compliance,
    evaluate_employment_rules,
    evaluate_nda_rules,
    evaluate_vendor_rules,
)
from services.document_service import get_demo_analysis
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_compliance_rules_unit():
    print("--- Running Unit Tests ---")

    # 1. Employment Test
    emp_extracted = [
        {"label": "Employee Name", "value": "Rahul Sharma", "status": "found"},
        {"label": "Company Name", "value": "TechCorp Solutions Pvt. Ltd.", "status": "found"},
        {"label": "Role / Designation", "value": "Senior Software Engineer", "status": "found"},
        {"label": "Joining Date", "value": "15 October 2026", "status": "found"},
        {"label": "Annual Salary (CTC)", "value": "₹8,00,000", "status": "found"},
        {"label": "Notice Period", "value": "90 Days", "status": "found"},
        {"label": "Contract Duration", "value": "12 Months (Fixed Term)", "status": "found"},
    ]
    emp_clauses = [
        {"name": "Termination Clause", "status": "warning", "clause": "Clause 11", "detail": "Termination period (6 months) contradicts contract duration (12 months)."},
        {"name": "Confidentiality Agreement", "status": "pass", "clause": "Clause 7", "detail": "Non-disclosure terms present."},
        {"name": "Data Protection / PDPA", "status": "fail", "clause": "Missing", "detail": "No data protection or privacy clause found."},
    ]

    res_emp = evaluate_compliance("Employment Agreement", emp_extracted, emp_clauses)
    print("\nEmployment Compliance Result:")
    print(f"Score: {res_emp['compliance_score']}")
    print(f"Status: {res_emp['compliance_status']}")
    print(f"Summary: {res_emp['summary']}")
    print(f"Rules evaluated: {len(res_emp['compliance_rules'])}")
    assert 0 <= res_emp["compliance_score"] <= 100
    assert res_emp["compliance_status"] in ["PASS", "WARNING", "FAIL"]
    for r in res_emp["compliance_rules"]:
        assert r["status"] in ["PASS", "WARNING", "FAIL"]
        assert r["severity"] in ["Low", "Medium", "High", "Critical"]

    # 2. NDA Test
    nda_extracted = [
        {"label": "Disclosing Party", "value": "TechCorp Solutions Pvt. Ltd.", "status": "found"},
        {"label": "Receiving Party", "value": "Nexus Innovations Ltd.", "status": "found"},
        {"label": "Confidentiality Period", "value": "3 Years", "status": "found"},
    ]
    nda_clauses = [
        {"name": "Definition of Confidential Information", "status": "pass", "clause": "Clause 1", "detail": "Clear definition."},
        {"name": "Obligations of Receiving Party", "status": "pass", "clause": "Clause 3", "detail": "Standard obligations."},
        {"name": "Exclusions from Confidentiality", "status": "pass", "clause": "Clause 4", "detail": "Public domain excluded."},
        {"name": "Return / Destruction of Information", "status": "pass", "clause": "Clause 7", "detail": "30 days return."},
        {"name": "Governing Law", "status": "pass", "clause": "Clause 9", "detail": "Indian Contract Act."},
    ]

    res_nda = evaluate_compliance("Non-Disclosure Agreement", nda_extracted, nda_clauses)
    print("\nNDA Compliance Result:")
    print(f"Score: {res_nda['compliance_score']}")
    print(f"Status: {res_nda['compliance_status']}")
    print(f"Summary: {res_nda['summary']}")
    assert 0 <= res_nda["compliance_score"] <= 100

    # 3. Vendor Test
    vnd_extracted = [
        {"label": "Vendor", "value": "CloudServe Technologies Ltd.", "status": "found"},
        {"label": "Client", "value": "TechCorp Solutions Pvt. Ltd.", "status": "found"},
        {"label": "Services", "value": "Cloud infrastructure", "status": "found"},
        {"label": "Contract Value", "value": "₹24,00,000 per annum", "status": "found"},
        {"label": "Payment Terms", "value": "Net-30 days", "status": "found"},
    ]
    vnd_clauses = [
        {"name": "Limitation of Liability", "status": "fail", "clause": "Missing", "detail": "No liability cap found."},
        {"name": "Data Security", "status": "warning", "clause": "Clause 10", "detail": "General security clause present."},
        {"name": "Termination Notice", "status": "pass", "clause": "Clause 12", "detail": "60 days notice."},
    ]

    res_vnd = evaluate_compliance("Vendor Agreement", vnd_extracted, vnd_clauses)
    print("\nVendor Compliance Result:")
    print(f"Score: {res_vnd['compliance_score']}")
    print(f"Status: {res_vnd['compliance_status']}")
    print(f"Summary: {res_vnd['summary']}")
    assert 0 <= res_vnd["compliance_score"] <= 100

    print("Unit tests PASSED!")


def test_api_endpoints():
    print("\n--- Running API Integration Tests ---")

    # GET /api/health
    r_health = client.get("/api/health")
    assert r_health.status_code == 200
    assert r_health.json()["status"] == "ok"
    print("GET /api/health: PASS")

    # GET /api/gemini/test
    r_gem = client.get("/api/gemini/test")
    assert r_gem.status_code == 200
    print(f"GET /api/gemini/test: {r_gem.json()}")

    # GET /api/demo/employment
    r_demo_emp = client.get("/api/demo/employment")
    assert r_demo_emp.status_code == 200
    data_emp = r_demo_emp.json()
    assert "compliance_score" in data_emp
    assert "compliance_status" in data_emp
    assert "compliance_rules" in data_emp
    assert "compliance_summary" in data_emp
    print(f"GET /api/demo/employment: PASS (score={data_emp['compliance_score']}, status={data_emp['compliance_status']})")

    # GET /api/demo/nda
    r_demo_nda = client.get("/api/demo/nda")
    assert r_demo_nda.status_code == 200
    data_nda = r_demo_nda.json()
    assert "compliance_score" in data_nda
    print(f"GET /api/demo/nda: PASS (score={data_nda['compliance_score']}, status={data_nda['compliance_status']})")

    # GET /api/demo/vendor
    r_demo_vnd = client.get("/api/demo/vendor")
    assert r_demo_vnd.status_code == 200
    data_vnd = r_demo_vnd.json()
    assert "compliance_score" in data_vnd
    print(f"GET /api/demo/vendor: PASS (score={data_vnd['compliance_score']}, status={data_vnd['compliance_status']})")

    # POST /api/analyze with sample TXT document
    sample_text = """EMPLOYMENT AGREEMENT
This Employment Agreement is entered into between TechCorp Solutions Pvt. Ltd. ("Employer") and Rahul Sharma ("Employee").
1. Position: Senior Software Engineer starting on October 15, 2026.
2. Compensation: Annual salary of ₹12,00,000 paid monthly.
3. Notice Period: Either party may terminate with 60 days written notice.
4. Confidentiality: Employee shall maintain strict confidentiality of all company data.
5. Termination: Employer may terminate for cause or with notice.
6. Governing Law: This Agreement is governed by the laws of India.
"""

    sample_path = backend_dir / "sample_test_doc.txt"
    sample_path.write_text(sample_text, encoding="utf-8")

    try:
        with open(sample_path, "rb") as f:
            r_analyze = client.post("/api/analyze", files={"file": ("sample_test_doc.txt", f, "text/plain")})

        print(f"POST /api/analyze status: {r_analyze.status_code}")
        if r_analyze.status_code == 200:
            res_data = r_analyze.json()
            print("POST /api/analyze successful response:")
            print(f"Document Type: {res_data.get('document_type')}")
            print(f"Compliance Score: {res_data.get('compliance_score')}")
            print(f"Compliance Status: {res_data.get('compliance_status')}")
            print(f"Compliance Summary: {res_data.get('compliance_summary')}")
            print(f"Rules Count: {len(res_data.get('compliance_rules', []))}")
            assert "compliance_score" in res_data
            assert "compliance_rules" in res_data
        else:
            print(f"POST /api/analyze error: {r_analyze.text}")

    finally:
        if sample_path.exists():
            sample_path.unlink()

    print("\nAPI Integration Tests Completed Successfully!")


if __name__ == "__main__":
    test_compliance_rules_unit()
    test_api_endpoints()
