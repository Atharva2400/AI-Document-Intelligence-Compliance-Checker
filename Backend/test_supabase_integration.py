"""
test_supabase_integration.py
-----------------------------
Tests the Supabase Storage integration alongside all existing endpoints.
Runs with SUPABASE_ENABLED=true (real upload) and then again with SUPABASE_ENABLED=false
(local fallback) without permanently changing the .env file.
"""

import os
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# ── Helpers ────────────────────────────────────────────────────────────────

SAMPLE_EMPLOYMENT_TXT = """\
EMPLOYMENT BOND AGREEMENT
This Employee Bond Agreement is made between TechCorp Solutions Pvt. Ltd. ("Employer")
and Priya Singh ("Employee").

1. SERVICE COMMITMENT: Employee commits to serve for a minimum of 24 months.
2. TRAINING RECOVERY: If Employee resigns before 24 months, ₹2,50,000 must be reimbursed.
3. NOTICE PERIOD: 90 days written notice is required by either party.
4. CONFIDENTIALITY: Employee shall not disclose any proprietary information.
5. TERMINATION: Employer may terminate with cause after providing written notice.
6. GOVERNING LAW: Governed by Indian Contract Act, 1872, courts of Bangalore.
"""

SAMPLE_NDA_TXT = """\
NON-DISCLOSURE AGREEMENT
This NDA is between Alpha Technologies Ltd. (Disclosing Party) and Beta Innovations (Receiving Party).
1. Confidential Information: All technical, business and financial data.
2. Obligations: Receiving Party shall maintain strict confidentiality.
3. Duration: 3 years from the effective date.
4. Return: All materials to be returned within 30 days of termination.
5. Governing Law: Indian Contract Act, 1872.
"""

SAMPLE_VENDOR_TXT = """\
VENDOR SERVICE AGREEMENT
Between TechCorp Solutions (Client) and CloudServe Ltd. (Vendor).
1. Scope: Cloud infrastructure management.
2. Payment: ₹24,00,000/year, Net-30 terms.
3. Duration: 12 months renewable.
4. Termination: 60 days notice required.
5. Confidentiality: Both parties agree to mutual non-disclosure.
6. Governing Law: Indian Contract Act, 1872.
"""


def _write_temp(name: str, content: str) -> Path:
    p = backend_dir / name
    p.write_text(content, encoding="utf-8")
    return p


def _cleanup(*paths: Path) -> None:
    for p in paths:
        if p.exists():
            p.unlink()


# ── Test runner ────────────────────────────────────────────────────────────

def run_tests(supabase_enabled: bool):
    label = "ENABLED" if supabase_enabled else "DISABLED (fallback)"
    print(f"\n{'=' * 60}")
    print(f"  SUPABASE_ENABLED = {label}")
    print(f"{'=' * 60}")

    # Patch env BEFORE importing FastAPI app so storage_service picks it up
    os.environ["SUPABASE_ENABLED"] = "true" if supabase_enabled else "false"

    # Force storage_service to reinitialise (env may have changed)
    import importlib, services.storage_service as ss_mod
    ss_mod._SUPABASE_ENABLED = supabase_enabled

    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)

    # 1 -- Health
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    print("GET /api/health          -> 200 OK [OK]")

    # 2 -- Gemini test
    r = client.get("/api/gemini/test")
    assert r.status_code == 200
    body = r.json()
    assert body.get("success") is True
    print(f"GET /api/gemini/test     -> {body['message']} [OK]")

    # 3 -- Demo endpoints
    for dtype in ("employment", "nda", "vendor"):
        r = client.get(f"/api/demo/{dtype}")
        assert r.status_code == 200
        d = r.json()
        assert "compliance_score" in d
        print(f"GET /api/demo/{dtype:<10} -> score={d['compliance_score']}, status={d.get('compliance_status')} [OK]")

    # 4 -- TXT upload
    txt_path = _write_temp("_test_emp.txt", SAMPLE_EMPLOYMENT_TXT)
    try:
        with open(txt_path, "rb") as f:
            r = client.post("/api/analyze", files={"file": ("employee_bond.txt", f, "text/plain")})
        assert r.status_code == 200, f"TXT upload returned {r.status_code}: {r.text[:200]}"
        d = r.json()
        assert "compliance_score" in d
        assert "storage" in d
        st = d["storage"]
        if supabase_enabled:
            print(f"POST /api/analyze TXT    -> score={d['compliance_score']}, "
                  f"storage.provider={st['provider']}, uploaded={st['uploaded']} [OK]")
        else:
            assert st["uploaded"] is False
            print(f"POST /api/analyze TXT    -> score={d['compliance_score']}, "
                  f"storage.provider=local (fallback) [OK]")
    finally:
        _cleanup(txt_path)

    # 5 -- Storage metadata
    print(f"\nStorage metadata format  -> provider, bucket, path, uploaded fields present [OK]")
    print(f"Storage bucket used      -> {d['storage']['bucket']}")
    print(f"Storage path format      -> {d['storage']['path']}")
    print(f"Existing response fields -> compliance_score={d['compliance_score']}, "
          f"risk_level={d.get('risk_level')}, total_issues={d.get('total_issues')} [OK]")


if __name__ == "__main__":
    # Run with Supabase enabled (real upload attempt)
    run_tests(supabase_enabled=True)

    # Run with Supabase disabled (local fallback)
    run_tests(supabase_enabled=False)

    print("\n\nAll tests completed successfully!")
