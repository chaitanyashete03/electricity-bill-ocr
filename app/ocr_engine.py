import cv2
import numpy as np
import easyocr
import fitz
import os
from PIL import Image

class OCREngine:
    def __init__(self):
        self.reader = easyocr.Reader(['mr', 'en'], gpu=False, verbose=False)

    def extract_text(self, file_path: str) -> str:
        extracted_text = ""
        try:
            if file_path.lower().endswith('.pdf'):
                doc = fitz.open(file_path)
                for page in doc:
                    # Render PDF page to image (pixmap)
                    pix = page.get_pixmap(dpi=300)
                    # Convert to numpy array
                    img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
                    if pix.n == 4: # RGBA
                        cv_img = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
                    else:
                        cv_img = img_array

                    result = self.reader.readtext(cv_img, detail=0)
                    extracted_text += "\n".join(result) + "\n"
                doc.close()
            else:
                result = self.reader.readtext(file_path, detail=0)
                extracted_text = "\n".join(result)
        except Exception as e:
            print(f"Error in OCR extraction: {e}")
            extracted_text = f"ERROR: {str(e)}"
            
        return extracted_text
