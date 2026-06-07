from app.models.schemas import AttestationVente
from mistralai import Mistral
from dotenv import load_dotenv
import os

load_dotenv()
MISTRAL_API_KEY=os.getenv("MISTRAL_API_KEY")
client=Mistral(api_key=MISTRAL_API_KEY)

def extract_data(text:str)->AttestationVente:
    res =  client.chat.complete(
        model="mistral-large-latest",
        messages=[
                    {
                        "content": f"""You are an expert in extracting structured data from French real estate documents (attestations de vente, mandats, EDD).

                        INSTRUCTIONS:
                        - Analyze the document text below and extract all relevant information
                        - Return ONLY a raw JSON object, no explanation, no backticks, no ```json``` markers
                        - The JSON must start with {{ and end with }}
                        - If a field is not found in the document, return null

                        JSON SCHEMA TO FOLLOW (use this as a guide, do NOT return the schema itself):
                        {AttestationVente.model_json_schema()}

                        DOCUMENT TO ANALYZE:
                        {text}
                        """,
                            "role": "user",
                        }
                    ]

    
        ).choices[0].message.content


    if res.startswith("```"):
        res = res.split("```")[1]
        if res.startswith("json"):
            res = res[4:]
    res = res.strip()
    return AttestationVente.model_validate_json(res)