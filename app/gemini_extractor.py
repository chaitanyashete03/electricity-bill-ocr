import os
import json
import mimetypes
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class GeminiExtractorEngine:
    def __init__(self):
        # Configure API key
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found. Please set it in Render Environment Variables.")
        
        # Use the new google-genai SDK (v1 API, not deprecated v1beta)
        self.client = genai.Client(api_key=self.api_key)
        self.model = 'gemini-flash-latest'
        
    def extract_from_file(self, file_path: str) -> dict:
        """
        Reads file bytes and sends them inline to Gemini for structured extraction.
        This avoids the File Upload API entirely for simpler, more reliable calls.
        """
        try:
            # Read file as bytes
            with open(file_path, 'rb') as f:
                file_bytes = f.read()
            
            # Auto-detect MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'image/jpeg' # Safe fallback

            prompt = """
            You are a highly accurate data extraction system. I will provide an image or pdf of an electricity bill.
            Extract the data strictly according to this JSON schema.
            For numbers like units, bill_amount, fixed_charges, or sanctioned_load, return ONLY digits and decimals (clean out letters, currency symbols, and commas).
            If a value is missing or completely illegible, leave the value empty string "".
            Estimate a confidence score between 0.0 and 1.0 (generally 0.95 if clearly visible).
            
            EXTREMELY IMPORTANT:
            Look at the bar chart/graph area reflecting the 12-month consumption history.
            Extract each month and its corresponding units into the 'consumption_history' array.
            Translate Marathi month names (e.g., नोव्हेबर, ऑक्टोबर) to English names (e.g., November, October).
            
            Output exact JSON format (no markdown, no code blocks):
            {
              "provider": "MSEDCL",
              "fields": {
                 "consumer_name": { "value": "", "confidence": 0.95 },
                 "consumer_number": { "value": "", "confidence": 0.95 },
                 "fixed_charges": { "value": "", "confidence": 0.95 },
                 "sanctioned_load": { "value": "", "confidence": 0.95 },
                 "connection_type": { "value": "", "confidence": 0.95 },
                 "units": { "value": "", "confidence": 0.95 },
                 "bill_amount": { "value": "", "confidence": 0.95 },
                 "bill_month": { "value": "", "confidence": 0.95 }
              },
              "consumption_history": [
                { "month": "English Month-Year", "units": 123, "confidence": 0.95 }
              ]
            }
            """
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                    prompt
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            try:
                data = json.loads(response.text)
                return data
            except json.JSONDecodeError:
                # Fallback processing if model still adds markdown blocks
                clean_text = response.text.replace("```json", "").replace("```", "").strip()
                data = json.loads(clean_text)
                return data

        except Exception as e:
            print(f"Error during Gemini Extraction: {e}")
            return {"error": str(e)}
