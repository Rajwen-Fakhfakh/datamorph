from app.models.schemas import AttestationVente
from mistralai import Mistral
from dotenv import load_dotenv
import os

load_dotenv()
MISTRAL_API_KEY=os.getenv("MISTRAL_API_KEY")
client=Mistral(api_key=MISTRAL_API_KEY)


def call_llm (text:str)->str: 

    output =  client.chat.complete(
        model="mistral-large-latest",
        messages=[
                    {
                        "role": "system",
                        "content": """You are an expert in extracting structured data from French real estate documents (attestations de vente, mandats, EDD)."""

                    },

                    {
                        "role": "user",
                        "content": f"""
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
                        """
                           
                        }
                    ],
        temperature=0, 
        max_tokens=1000           

    
        ).choices[0].message.content


    if output.startswith("```"):
        output = output.split("```")[1]
        if output.startswith("json"):
            output = output[4:]
    output = output.strip()
    return output


def extract_data(text:str,max_retries:int=3)->AttestationVente:

    last_exception = None

    for attempt in range(max_retries):     
        
        output = call_llm(text)
        try:
            return AttestationVente.model_validate_json(output)
        except Exception as e:
            last_exception = e
            print(f"Error validating JSON: Error Exception : {last_exception} , Attempt {attempt + 1} / {max_retries}")

    raise ValueError({"error": "Unable to validate extracted data after all retries. Please check the document format and content.", "details": str(last_exception)})