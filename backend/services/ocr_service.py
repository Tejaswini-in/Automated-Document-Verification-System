import pytesseract
from PIL import Image
import os
from pdf2image import convert_from_path


# Set correct paths
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\User\Downloads\tesseract.exe"
poppler_path = r"C:\Users\User\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin"  # Change to your actual Poppler path

def extract_text(file_path):
    try:
        print("📄 [OCR] File path received:", file_path)
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            print("[OCR] Detected PDF. Converting to images...")
            images = convert_from_path(file_path, poppler_path=poppler_path)
            print(f"[OCR] Total pages converted: {len(images)}")

            text = ""
            for i, img in enumerate(images):
                page_text = pytesseract.image_to_string(img)
                text += f"\n\n[Page {i+1}]\n" + page_text
            print("[OCR] OCR completed for PDF.")
            return text

        else:
            print("[OCR] Detected image. Running OCR...")
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)
            print("[OCR] OCR completed for image.")
            return text

    except Exception as e:
        print("[OCR ERROR]", str(e))
        return "ERROR: " + str(e)
