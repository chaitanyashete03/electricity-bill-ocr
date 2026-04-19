import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiExtractorEngine:
    def __init__(self):
        # Configure API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("WARNING: GEMINI_API_KEY not found in environment and .env")
        genai.configure(api_key=api_key)
        
        # Use gemini-flash-latest for very fast, accurate multimodal extraction
        self.model = genai.GenerativeModel('gemini-flash-latest')
        
    def extract_from_file(self, file_path: str) -> dict:
        """
        Uploads a file to Gemini and extracts structured JSON details.
        Returns a tuple/dict with provider and extracted fields.
        """
        try:
            # Upload the file to Gemini API
            sample_file = genai.upload_file(path=file_path)
            
            prompt = """
            You are a highly accurate data extraction system. I will provide an image or pdf of an electricity bill.
            Extract the data strictly according to this JSON schema.
            For numbers like units, bill_amount, fixed_charges, or sanctioned_load, return ONLY digits and decimals (clean out letters, currency symbols, and commas).
            If a value is missing or completely illegible, leave the value empty string "".
            Estimate a confidence score between 0.0 and 1.0 (generally 0.95 if clearly visible).
            
            Output exact JSON format:
            {
              "provider": "MSEDCL", // MSEDCL, BSES, TATA, or Other
              "fields": {
                 "consumer_name": { "value": "", "confidence": 0.95 },
                 "consumer_number": { "value": "", "confidence": 0.95 },
                 "fixed_charges": { "value": "", "confidence": 0.95 },
                 "sanctioned_load": { "value": "", "confidence": 0.95 },
                 "connection_type": { "value": "", "confidence": 0.95 },
                 "units": { "value": "", "confidence": 0.95 },
                 "bill_amount": { "value": "", "confidence": 0.95 },
                 "bill_month": { "value": "", "confidence": 0.95 }
              }
            }
            """
            
            response = self.model.generate_content(
                [sample_file, prompt],
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            
            # Clean up the file from GenAI servers to preserve privacy/quota
            sample_file.delete()
            
            try:
                data = json.loads(response.text)
                return data
            except json.JSONDecodeError:
                # Fallback processing if markdown block used despite prompt
                clean_text = response.text.replace("```json", "").replace("```", "").strip()
                data = json.loads(clean_text)
                return data

        except Exception as e:
            print(f"Error during Gemini Extraction: {e}")
            return {"error": str(e)}
