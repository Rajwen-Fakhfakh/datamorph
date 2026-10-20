from google.genai import types
from pydantic import ValidationError

from app.models.schemas import AttestationVente
from app.services.gemini_client import GEMINI_MODEL, client


def call_llm (text:str)->str:

    output = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=f"""
                        Analyze the document text below step by step :
                        1-Identify the document type
                        2-Extract the relevant information according to the JSON schema provided in the instructions
                        3-Return the extracted information in a raw JSON format that strictly follows the provided schema.

                        INSTRUCTIONS:
                        - Return ONLY a raw JSON object, no explanation, no backticks, no ```json``` markers
                        - The JSON must start with {{ and end with }}
                        - If a field is not found in the document, return null

                        JSON SCHEMA TO FOLLOW (use this as a guide, do NOT return the schema itself):
                        {AttestationVente.model_json_schema()}

                        DOCUMENT TO ANALYZE:
                        {text}
                        """,
        config=types.GenerateContentConfig(
            system_instruction="You are an expert in extracting structured data from French real estate documents (attestations de vente, mandats, EDD).",
            response_mime_type="application/json",  # force une sortie JSON valide (plus de backticks à nettoyer)
            temperature=0,
            max_output_tokens=8192,
        ),
    ).text

    return (output or "").strip()


def extract_data(text:str,max_retries:int=3)->AttestationVente:

    last_exception = None

    for attempt in range(max_retries):     
        
        output = call_llm(text)
        try:
            return AttestationVente.model_validate_json(output)
        except ValidationError as e:
            last_exception = e
            print(f"Error validating JSON: Error Exception : {last_exception} , Attempt {attempt + 1} / {max_retries}")

    raise ValueError({"error": "Unable to validate extracted data after all retries. Please check the document format and content.", "details": str(last_exception)})