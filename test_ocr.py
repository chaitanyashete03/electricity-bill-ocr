import easyocr

print("Loading model for Marathi and English...")
reader = easyocr.Reader(['mr', 'en'], gpu=False)
print("Extracting text from E BILL.jpeg...")
results = reader.readtext("E BILL.jpeg", detail=0)
print("\n--- EXTRACTED TEXT ---")
for i, line in enumerate(results):
    print(f"[{i:02d}] {line}")
