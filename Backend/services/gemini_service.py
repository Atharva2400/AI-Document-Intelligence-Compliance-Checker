import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured")

client = genai.Client(
    vertexai=True,
    api_key=API_KEY
)


def test_gemini():
    response = client.models.generate_content(
        model=MODEL,
        contents="Reply with exactly: Gemini connection successful."
    )

    return response.text


def analyze_document_with_gemini(document_text: str) -> dict:
    """
    Sends extracted document text to Gemini and requests ONLY valid JSON.
    Returns parsed dictionary matching the Gemini output schema.
    """
    max_chars = 60000
    if len(document_text) > max_chars:
        document_text = document_text[:max_chars] + "\n\n[Document text truncated due to length limits]"

    prompt = f"""You are an expert legal and document compliance analysis AI.
Analyze the following document text and return ONLY a valid JSON object matching this exact schema:

{{
  "document_type": "string (e.g. Employment Agreement, Non-Disclosure Agreement, Vendor Agreement, Service Level Agreement, Policy, Contract, Unknown)",
  "confidence": 0,
  "extracted_information": {{
    "Key Field Name": "Extracted Value"
  }},
  "clauses": [
    {{
      "name": "Clause Name",
      "status": "pass",
      "clause": "Clause 1.0",
      "detail": "Description of clause"
    }}
  ],
  "missing_clauses": [
    {{
      "name": "Missing Clause Name",
      "status": "fail",
      "clause": "Missing",
      "detail": "Explanation why it is missing and required"
    }}
  ],
  "contradictions": [
    {{
      "id": "CON-001",
      "title": "Title of contradiction",
      "confidence": 90,
      "risk": "HIGH",
      "severity": "CRITICAL",
      "clause1": {{ "id": "Clause 1", "title": "Title 1", "text": "Text 1" }},
      "clause2": {{ "id": "Clause 2", "title": "Title 2", "text": "Text 2" }},
      "evidence": "Evidence explanation",
      "impact": "Impact explanation",
      "recommendation": "Recommendation"
    }}
  ],
  "findings": [
    {{
      "id": "CR-001",
      "rule": "Rule name",
      "category": "Category",
      "status": "pass",
      "severity": "HIGH",
      "evidence": "Evidence quote",
      "recommendation": "Recommendation text"
    }}
  ],
  "recommendations": [
    {{
      "priority": 1,
      "severity": "HIGH",
      "title": "Short title",
      "action": "Detailed action item"
    }}
  ]
}}

Rules:
1. Do not invent facts. Base analysis strictly on the document text.
2. Use null/empty arrays/objects when information is unavailable or not present.
3. Status must strictly be "pass", "warning", or "fail".
4. Severity must strictly be "CRITICAL", "HIGH", "MEDIUM", or "LOW".
5. Confidence must be an integer between 0 and 100.
6. Return JSON only.

Document Text:
{document_text}
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.0,
        )
    )

    raw_text = response.text.strip()
    if raw_text.startswith("```"):
        lines = raw_text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        raw_text = "\n".join(lines).strip()

    try:
        data = json.loads(raw_text)
        return data
    except Exception as e:
        raise RuntimeError(f"Failed to parse JSON response from Gemini: {e}. Raw text: {raw_text[:200]}")