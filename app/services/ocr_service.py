import fitz
import base64
from mistralai import Mistral
from dotenv import load_dotenv
import os

load_dotenv()
MISTRAL_API_KEY=os.getenv("MISTRAL_API_KEY")
client=Mistral(api_key=MISTRAL_API_KEY)

def client_ocr(image_b64:str)->str:
   return  client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "image_url",
        "image_url": f"data:image/png;base64,{image_b64}"
    },
  
).pages[0].markdown

def extract_text_from_pdf(path:str)->str: 
    document=fitz.open(path)
    res=""
    for page in document:

        img_bytes=page.get_pixmap().tobytes() # convert the image to bytes
        img_b64=base64.b64encode(img_bytes).decode('utf-8') # encode the bytes to base64 string
              


        res+= client_ocr(img_b64) #res from mistral ocr
    return res

