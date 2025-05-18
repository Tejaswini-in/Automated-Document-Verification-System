import pytesseract
from PIL import Image
import os
from pdf2image import convert_from_path


# Set correct paths
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
poppler_path = r"C:\Users\User\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin"  # Change to your actual Poppler path

def extract_text_from_image(image_path):
    """
    Extract text from an image file.
    
    Args:
        image_path (str): Path to the image file
    
    Returns:
        str: Extracted text from the image
    """
    try:
        print(f"[OCR DEBUG] Processing image: {image_path}")
        print(f"[OCR DEBUG] Tesseract path: {pytesseract.pytesseract.tesseract_cmd}")
        print(f"[OCR DEBUG] File exists: {os.path.exists(image_path)}")
        
        # Open the image
        img = Image.open(image_path)
        print(f"[OCR DEBUG] Image size: {img.size}")
        print(f"[OCR DEBUG] Image mode: {img.mode}")
        
        # Extract text from the image
        print("[OCR DEBUG] Starting text extraction...")
        text = pytesseract.image_to_string(img)
        print(f"[OCR DEBUG] Extracted text length: {len(text)}")
        print("[OCR DEBUG] First 200 characters of extracted text:")
        print(text[:200])
        
        return text.strip()
    except Exception as e:
        print(f"[OCR ERROR] Failed to process image: {str(e)}")
        return f"Error processing {image_path}: {str(e)}"
    
def extract_text(file_path):
    try:
        print("📄 [OCR] File path received:", file_path)
        print(f"[OCR DEBUG] File exists: {os.path.exists(file_path)}")
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            print("[OCR] Detected PDF. Converting to images...")
            print(f"[OCR DEBUG] Poppler path: {poppler_path}")
            print(f"[OCR DEBUG] Poppler exists: {os.path.exists(poppler_path)}")
            images = convert_from_path(file_path, poppler_path=poppler_path)
            print(f"[OCR] Total pages converted: {len(images)}")

            text = ""
            for i, img in enumerate(images):
                print(f"[OCR DEBUG] Processing PDF page {i+1}")
                page_text = pytesseract.image_to_string(img)
                text += f"\n\n[Page {i+1}]\n" + page_text
            print("[OCR] OCR completed for PDF.")
            print(f"[OCR DEBUG] Total extracted text length: {len(text)}")
            return text

        else:
            print("[OCR] Detected image. Running OCR...")
            img = Image.open(file_path)
            print(f"[OCR DEBUG] Image size: {img.size}")
            print(f"[OCR DEBUG] Image mode: {img.mode}")
            text = pytesseract.image_to_string(img)
            print("[OCR] OCR completed for image.")
            print(f"[OCR DEBUG] Extracted text length: {len(text)}")
            return text

    except Exception as e:
        print("[OCR ERROR]", str(e))
        return "ERROR: " + str(e)
