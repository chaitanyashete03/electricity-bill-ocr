class ValidationEngine:
    def __init__(self):
        pass

    def validate_fields(self, extracted_data: dict) -> dict:
        results = extracted_data.copy()
        
        # Validate Units
        units_val = results.get("units", {}).get("value", "")
        if units_val:
            try:
                units = float(units_val)
                if not (0 <= units <= 5000):
                    results["units"]["flag"] = True
                    results["units"]["issue"] = "Units out of bounds (0-5000)"
            except ValueError:
                results["units"]["flag"] = True
                results["units"]["issue"] = "Units must be numeric"

        # Validate Bill Amount
        bill_val = results.get("bill_amount", {}).get("value", "")
        if bill_val:
            try:
                bill = float(bill_val)
                if bill < 0:
                    results["bill_amount"]["flag"] = True
                    results["bill_amount"]["issue"] = "Bill amount cannot be negative"
            except ValueError:
                results["bill_amount"]["flag"] = True
                results["bill_amount"]["issue"] = "Bill amount must be numeric"

        # Validate Sanctioned Load
        load_val = results.get("sanctioned_load", {}).get("value", "")
        if load_val:
            try:
                float(load_val) # must be numeric
            except ValueError:
                results["sanctioned_load"]["flag"] = True
                results["sanctioned_load"]["issue"] = "Sanctioned load must be numeric"
                
        # Confidence Score
        overall_confidence = 0.0
        count = 0
        for k, data in results.items():
            if isinstance(data, dict) and "confidence" in data:
                conf_val = data.get("confidence", 0.0)
                # Normalize if Gemini returns 0-100 instead of 0.0-1.0
                if conf_val > 1.0:
                    conf_val = conf_val / 100.0
                    data["confidence"] = conf_val # fix it in the payload too
                overall_confidence += conf_val
                count += 1
                
        if count > 0:
            overall_confidence = (overall_confidence / count) * 100 # output as a percentage string ultimately
        else:
            overall_confidence = 95.0
            
        review_required = overall_confidence < 75.0 or any(d.get("flag", False) for k, d in results.items() if isinstance(d, dict))
            
        return {
            "fields": results,
            "overall_confidence": overall_confidence,
            "review_required": review_required
        }
