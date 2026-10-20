from google.genai import types

from app.services.gemini_client import GEMINI_MODEL, client

OCR_PROMPT = """Transcribe the full text of this document faithfully, page by page, in Markdown.
Keep tables, amounts, dates, names and identifiers exactly as written.
Return only the transcription, with no comment."""


def extract_text_from_pdf(path: str) -> str:
    # Gemini lit les PDF nativement (y compris scannés) : une seule requête pour tout le document
    with open(path, "rb") as f:
        pdf_bytes = f.read()

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[
            types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
            OCR_PROMPT,
        ],
        config=types.GenerateContentConfig(temperature=0),
    )
    return response.text or ""
