import re
import json

class ExtractorEngine:
    def __init__(self, config_path="app/utility_patterns.json"):
        self.config_path = config_path

    def extract_fields(self, provider: str, text: str) -> dict:
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
            
        result = {}
        if provider not in self.config:
            provider = "MSEDCL" # Fallback rule
            
        provider_config = self.config[provider]
        fields = [
            "consumer_name", "consumer_number", "fixed_charges", 
            "sanctioned_load", "connection_type", "units", 
            "bill_amount", "bill_month"
        ]
        # Normalize text: Marathi numbers to English, '!' to '.' in numbers, etc.
        marathi_to_eng = str.maketrans('०१२३४५६७८९', '0123456789')
        text = text.translate(marathi_to_eng)
        text = re.sub(r'(\d)\s*!\s*(\d)', r'\1.\2', text) # Fix 540!00
        text = re.sub(r'(\d)\s*\|\s*(\d)', r'\1\2', text) # Fix 0912 | 506 -> 0912506
        
        for field in fields:
            extracted_val = ""
            confidence = 0.0
            
            if field in provider_config:
                patterns = provider_config[field].get("patterns", [])
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        extracted_val = " ".join(g for g in match.groups() if g).strip()
                        confidence = 0.90 # High confidence on regex match
                        break
            
            # Simple cleanup for numbers
            if field == "units" and extracted_val:
                extracted_val = re.sub(r'[^\d]', '', extracted_val)
            elif field in ["fixed_charges", "bill_amount", "sanctioned_load"] and extracted_val:
                extracted_val = re.sub(r'[^\d\.]', '', extracted_val)
                
            if not extracted_val:
                confidence = 0.0
                
            result[field] = {
                "value": extracted_val,
                "confidence": confidence
            }
            
        return result
