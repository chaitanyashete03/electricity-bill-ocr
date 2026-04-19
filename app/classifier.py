import json
import os

class DocumentClassifier:
    def __init__(self, config_path="app/utility_patterns.json"):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

    def classify_provider(self, text: str) -> str:
        text_lower = text.lower()
        for provider, data in self.config.items():
            for kw in data.get("keywords", []):
                if kw.lower() in text_lower:
                    return provider
        return "GENERIC"
