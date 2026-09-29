import os

from dotenv import load_dotenv
from google import genai

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