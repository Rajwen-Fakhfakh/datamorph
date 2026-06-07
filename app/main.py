from fastapi import FastAPI,UploadFile
from app.services.ocr_service import extract_text_from_pdf
from app.services.llm_service import extract_data
import os

app = FastAPI()


@app.get("/Health")
def read_health():
    return {"message": "Hello, World!"}


@app.post("/extract")
def extract(file: UploadFile):
    os.makedirs("temp", exist_ok=True)
    file_path=f"temp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    ocrText = extract_text_from_pdf(file_path) # extract text from pdf and return the result
    print("text: ",ocrText)
    data = extract_data(ocrText) # extract data from text and return the result
    os.remove(file_path)    
    return data

