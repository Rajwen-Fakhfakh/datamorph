from fastapi import FastAPI, HTTPException,UploadFile
from app.services.ocr_service import extract_text_from_pdf
from app.services.llm_service import extract_data
import os

app = FastAPI()


@app.get("/Health")
def read_health():
    return {"message": "Hello, World!"}


@app.post("/extract")
def extract(file: UploadFile):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail={"error": "Invalid file type. Please upload a PDF."})

    os.makedirs("temp", exist_ok=True)
    file_path=f"temp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    ocrText = extract_text_from_pdf(file_path) # extract text from pdf and return the result

    if(ocrText is None or ocrText.strip() == ""):
        os.remove(file_path)
        raise HTTPException(status_code=400, detail={"error": "Unable to extract text from the PDF. Please ensure the document is clear and try again."})
    
    try:

        data = extract_data(ocrText) # extract data from text and return the result

    except ValueError as e:
        os.remove(file_path)
        raise HTTPException(status_code=422, detail={"error": str(e)})


    os.remove(file_path)
    return data

