import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import cv2
import numpy as np

# Placeholder function to handle document verification
def verify_document(doc_path, doc_type):
    try:
        # Step 1: Process the document based on its type (image or PDF)
        if doc_path.lower().endswith('.pdf'):
            # Convert PDF to images (one image per page)
            images = convert_from_path(doc_path)
            extracted_text = ''
            for image in images:
                extracted_text += pytesseract.image_to_string(image)
        else:
            # Process image files directly
            image = Image.open(doc_path)
            extracted_text = pytesseract.image_to_string(image)

        # Step 2: Mock verification logic based on document type
        if doc_type == 'aadhaar':
            status = "Verified" if "Aadhaar" in extracted_text else "Rejected"
        elif doc_type == 'pan':
            status = "Verified" if "PAN" in extracted_text else "Rejected"
        elif doc_type == 'driving_license':
            status = "Verified" if "DL" in extracted_text else "Rejected"
        elif doc_type == 'voter_id':
            status = "Verified" if "Voter" in extracted_text else "Rejected"
        elif doc_type == 'passport':
            status = "Verified" if "Passport" in extracted_text else "Rejected"
        else:
            status = "Rejected"

        # Log the extracted text for debugging purposes
        print(f"Extracted Text for {doc_type}: {extracted_text}")
        return status, extracted_text

    except Exception as e:
        print(f"[ERROR] Document verification failed: {str(e)}")
        return "Rejected", str(e)
