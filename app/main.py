from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os
from tempfile import NamedTemporaryFile
import json

from app.gemini_extractor import GeminiExtractorEngine
from app.validator import ValidationEngine
from app.excel_engine import ExcelEngine
from fastapi import Request

ACCESS_KEY = os.getenv("ENERGYBAE_ACCESS_KEY", "energy2026") # Default for demo

app = FastAPI()

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

gemini_extractor = GeminiExtractorEngine()
validator = ValidationEngine()
excel_gen = ExcelEngine()

@app.post("/login")
async def login(data: dict):
    if data.get("key") == ACCESS_KEY:
        return {"status": "success"}
    raise HTTPException(status_code=401, detail="Invalid Access Key")

@app.get("/")
def serve_home():
    return FileResponse("static/index.html")

def verify_access(request: Request):
    key = request.headers.get("X-Access-Key")
    if key != ACCESS_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/upload")
async def process_bill(request: Request, file: UploadFile = File(...)):
    verify_access(request)
    if not file.filename.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg')):
        raise HTTPException(400, "Unsupported file format.")
        
    temp_file = NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])
    try:
        content = await file.read()
        temp_file.write(content)
        temp_file.close()

        # Extract structured data directly with Gemini
        gemini_result = gemini_extractor.extract_from_file(temp_file.name)
        if "error" in gemini_result:
            raise HTTPException(500, f"Gemini Extraction failed: {gemini_result['error']}")
        
        provider = gemini_result.get("provider", "Unknown")
        extracted_fields = gemini_result.get("fields", {})
        
        # Validate logic remains the same to catch out-of-bounds metrics
        validation_result = validator.validate_fields(extracted_fields)
        validation_result["provider"] = provider
        
        return JSONResponse(validation_result)
        
    finally:
        os.unlink(temp_file.name)

@app.post("/generate")
def generate_excel(request: Request, data: dict):
    verify_access(request)
    output_path = "Output_E-Bill.xlsx"
    fields = data.get("fields", {})
    try:
        excel_gen.generate_dynamic_excel(fields, output_path)
    except Exception as e:
        raise HTTPException(500, f"Error generating Excel: {str(e)}")
        
    return {"message": "Excel generated successfully", "download_url": "/download"}

@app.get("/download")
def download_excel():
    output_path = "Output_E-Bill.xlsx"
    if os.path.exists(output_path):
        return FileResponse(output_path, filename="Updated_E-Bill_Analysis.xlsx")
    raise HTTPException(404, "File not found.")
