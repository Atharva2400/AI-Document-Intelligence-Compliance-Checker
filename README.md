# AI Document Intelligence — Backend

FastAPI backend for the **AI Document Intelligence & Compliance Checker**.

> **Phase 1** — all analysis is mock data.  
> **Phase 2** — will connect to Google Cloud Storage → Vertex AI / Gemini → Compliance Engine.

---

## Project Structure

```
Backend/
├── main.py                   ← FastAPI app + all route definitions
├── requirements.txt          ← Python dependencies
├── .env.example              ← Copy to .env and customise
├── uploads/                  ← Uploaded files saved here temporarily
├── models/
│   └── schemas.py            ← Pydantic request / response models
├── services/
│   ├── document_service.py   ← Business logic (validation, file save, analysis)
│   ├── gemini_service.py     ← Google Gemini API extraction integration
│   └── compliance_service.py ← Custom Python Compliance Rule Engine
└── data/
    └── mock_analysis.py      ← Realistic mock data for all 3 document types

---

## Compliance Engine

- **Gemini performs extraction**: Gemini analyzes raw text and returns structured fields, clauses, and contradictions.
- **Python performs deterministic compliance checks**: `compliance_service.py` evaluates document-specific compliance rules (Employment, NDA, Vendor).
- **Rules return PASS / WARNING / FAIL**: Each rule outputs a status, severity (Low, Medium, High, Critical), evidence, and recommendation.
- **Compliance score is calculated by Python**: A transparent formula calculates the 0-100 score (PASS = 100%, WARNING = 50%, FAIL = 0%).
```

---

## Quick Start

### 1 — Create a virtual environment

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 2 — Install dependencies

```bash
pip install -r requirements.txt
```

### 3 — Configure environment (optional for Phase 1)

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Edit `.env` if you need to change the port or allowed origins.

### 4 — Run the server

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

### 5 — Open interactive API docs

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/docs | Swagger UI — test all endpoints in browser |
| http://127.0.0.1:8000/redoc | ReDoc — clean API reference |

---

## API Reference

### `GET /api/health`
Confirm the server is running.

```json
{ "status": "ok", "version": "1.0.0", "message": "AI Document Intelligence API is running" }
```

---

### `POST /api/analyze`
Upload a document and receive a full analysis.

**Request** — `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | File | ✅ | PDF, DOCX or TXT — max 50 MB |

**Test with curl:**
```bash
curl -X POST http://127.0.0.1:8000/api/analyze \
  -F "file=@/path/to/Employment_Agreement.pdf"
```

**Test with PowerShell:**
```powershell
$form = @{ file = Get-Item "C:\path\to\Employment_Agreement.pdf" }
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/analyze" -Method Post -Form $form
```

**Response** (truncated):
```json
{
  "document_name": "Employment_Agreement.pdf",
  "document_type": "Employment Agreement",
  "confidence": 94,
  "compliance_score": 83,
  "risk_level": "HIGH",
  "risk_score": 78,
  "total_issues": 7,
  "critical_issues": 1,
  "extracted_information": [...],
  "clauses": [...],
  "compliance_rules": [...],
  "contradictions": [...],
  "recommendations": [...]
}
```

---

### `GET /api/demo/{document_type}`
Get a mock analysis without uploading a file.

| `document_type` | Returns |
|-----------------|---------|
| `employment` | Employment Agreement analysis |
| `nda` | Non-Disclosure Agreement analysis |
| `vendor` | Vendor / Service Agreement analysis |

```bash
curl http://127.0.0.1:8000/api/demo/employment
curl http://127.0.0.1:8000/api/demo/nda
curl http://127.0.0.1:8000/api/demo/vendor
```

---

### `GET /api/demo-types`
List all available demo document types.

---

## Frontend Connection

The React frontend (Vite) is configured to proxy all `/api/*` requests to this
backend. Make sure the backend is running on port **8000** before starting the
frontend dev server:

```bash
# Terminal 1 — Backend
cd Backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2 — Frontend
cd Frontend
npm run dev
```

Frontend dev server: **http://localhost:5173**  
Backend API: **http://127.0.0.1:8000**  
API Docs: **http://127.0.0.1:8000/docs**

---

## Error Responses

All errors return a consistent JSON envelope:

```json
{
  "error": "Unsupported file type '.exe'. Allowed types: .docx, .pdf, .txt",
  "detail": null,
  "status_code": 400
}
```

| Code | Meaning |
|------|---------|
| 400 | Bad request — invalid file type or malformed input |
| 404 | Demo document type not found |
| 413 | File too large (> 50 MB) |
| 500 | Unexpected server error |

---

## Future Architecture (Phase 2)

```
React Frontend
    ↓  POST /api/analyze
FastAPI Backend (this repo)
    ↓  upload file
Google Cloud Storage
    ↓  trigger processing
Vertex AI / Gemini
    ↓  extracted text + classification
Compliance & Risk Engine
    ↓  structured analysis result
FastAPI Backend
    ↓  JSON response
React Frontend
```
