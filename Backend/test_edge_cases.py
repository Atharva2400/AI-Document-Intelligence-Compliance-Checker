"""
test_edge_cases.py
-------------------
Tests edge cases, document classification routing, and compliance failure graceful handling.
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.compliance_service import evaluate_compliance
from services.document_service import _convert_gemini_to_analysis_response
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_nda_real_doc():
    print("--- Testing NDA Document Analysis ---")
    nda_text = """MUTUAL NON-DISCLOSURE AGREEMENT
This Non-Disclosure Agreement ("Agreement") is made on September 1, 2026, by and between TechCorp Solutions Pvt. Ltd. ("Disclosing Party") and Nexus Innovations Ltd. ("Receiving Party").
1. Confidential Information: All technical, business, and financial information disclosed.
2. Obligations: The Receiving Party shall hold all Confidential Information in strict confidence.
3. Exclusions: Information in the public domain or previously known is excluded.
4. Duration: This Agreement shall remain effective for a period of 3 years from the Effective Date.
5. Return of Materials: Upon request or termination, Receiving Party shall return all materials within 30 days.
6. Governing Law: Governed by the laws of India, courts of Bangalore.
"""
    sample_path = backend_dir / "sample_nda.txt"
    sample_path.write_text(nda_text, encoding="utf-8")

    try:
        with open(sample_path, "rb") as f:
            res = client.post("/api/analyze", files={"file": ("sample_nda.txt", f, "text/plain")})

        assert res.status_code == 200
        data = res.json()
        print(f"Document Type Detected: {data['document_type']}")
        print(f"Compliance Score: {data['compliance_score']}")
        print(f"Compliance Status: {data['compliance_status']}")
        print(f"Compliance Rules Count: {len(data['compliance_rules'])}")
        assert data['compliance_score'] is not None
        assert 0 <= data['compliance_score'] <= 100
        assert data['compliance_status'] in ["PASS", "WARNING", "FAIL"]
    finally:
        if sample_path.exists():
            sample_path.unlink()


def test_vendor_real_doc():
    print("\n--- Testing Vendor Agreement Analysis ---")
    vendor_text = """VENDOR SERVICE AGREEMENT
This Vendor Agreement is entered into between TechCorp Solutions Pvt. Ltd. ("Client") and CloudServe Technologies Ltd. ("Vendor").
1. Scope of Services: Vendor shall provide cloud infrastructure and DevOps management services.
2. Payment Terms: Client shall pay ₹24,00,000 per annum on Net-30 day terms.
3. Term: Fixed duration of 12 months starting October 1, 2026.
4. Termination: Either party may terminate with 60 days written notice.
5. Confidentiality: Both parties agree to maintain confidentiality of business data.
6. Governing Law: Governed by Indian Contract Act, 1872.
"""
    sample_path = backend_dir / "sample_vendor.txt"
    sample_path.write_text(vendor_text, encoding="utf-8")

    try:
        with open(sample_path, "rb") as f:
            res = client.post("/api/analyze", files={"file": ("sample_vendor.txt", f, "text/plain")})

        assert res.status_code == 200
        data = res.json()
        print(f"Document Type Detected: {data['document_type']}")
        print(f"Compliance Score: {data['compliance_score']}")
        print(f"Compliance Status: {data['compliance_status']}")
        print(f"Compliance Rules Count: {len(data['compliance_rules'])}")
        assert data['compliance_score'] is not None
        assert 0 <= data['compliance_score'] <= 100
    finally:
        if sample_path.exists():
            sample_path.unlink()


def test_compliance_failure_fallback():
    print("\n--- Testing Graceful Fallback when Compliance Engine Errors ---")
    mock_gemini_output = {
        "document_type": "Unknown Document",
        "confidence": 80,
        "extracted_information": {"Field": "Value"},
        "clauses": []
    }

    # Simulate compliance engine raising an exception
    original_eval = sys.modules["services.document_service"].evaluate_compliance

    def mock_broken_eval(*args, **kwargs):
        raise RuntimeError("Simulated internal rule engine failure")

    sys.modules["services.document_service"].evaluate_compliance = mock_broken_eval

    try:
        res = _convert_gemini_to_analysis_response(mock_gemini_output, "test_file.txt", 100)
        print(f"Graceful response on failure:")
        print(f"  compliance_score: {res['compliance_score']}")
        print(f"  compliance_status: {res['compliance_status']}")
        print(f"  compliance_summary: {res['compliance_summary']}")
        assert res["compliance_score"] is None
        assert res["compliance_status"] == "UNAVAILABLE"
        assert "Simulated internal rule engine failure" in res["compliance_summary"]
        assert res["document_name"] == "test_file.txt"
        print("Fallback test PASSED!")
    finally:
        sys.modules["services.document_service"].evaluate_compliance = original_eval


if __name__ == "__main__":
    test_nda_real_doc()
    test_vendor_real_doc()
    test_compliance_failure_fallback()
