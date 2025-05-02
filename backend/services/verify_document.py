import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import re
from difflib import SequenceMatcher
import cv2
import numpy as np

def clean_text(text):
    """Remove non-alphanumeric characters and normalize whitespace."""
    return re.sub(r'[^a-zA-Z0-9\s]', '', text).lower()

def fuzzy_match(text, keyword, threshold=0.7):
    """
    Check if any sliding chunk of words in the text matches the keyword above a similarity threshold.
    """
    text = clean_text(text)
    keyword = clean_text(keyword)
    words = text.split()
    kw_len = len(keyword.split())

    for i in range(len(words) - kw_len + 1):
        chunk = ' '.join(words[i:i + kw_len])
        similarity = SequenceMatcher(None, keyword, chunk).ratio()
        if similarity >= threshold:
            return True
    return False


def preprocess_image(path):
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return Image.fromarray(thresh)


def verify_document(doc_path, doc_type):
    try:
        # Step 1: OCR - Extract text from image or PDF
        if doc_path.lower().endswith('.pdf'):
            images = convert_from_path(doc_path)
            extracted_text = ''
            for image in images:
                extracted_text += pytesseract.image_to_string(image, config='--psm 6')
        else:
            image = preprocess_image(doc_path)
            extracted_text = pytesseract.image_to_string(image, config='--psm 6')

        extracted_text = extracted_text.upper()
        status = "Rejected"

        # Aadhaar
        if doc_type == 'aadhaar':
            aadhaar_keywords = ["AADHAAR", "UNIQUE IDENTIFICATION", "VID", "GOVERNMENT OF INDIA"]
            aadhaar_number = re.search(r'\b\d{4}\s\d{4}\s\d{4}\b', extracted_text)
            if any(fuzzy_match(extracted_text, k) for k in aadhaar_keywords) and aadhaar_number:
                status = "Verified as Aadhaar Card"
            else:
                status = "Invalid document for Aadhaar Card"

        # PAN
        elif doc_type == 'pan':
            pan_keywords = ["INCOME TAX DEPARTMENT", "PERMANENT ACCOUNT NUMBER", "INCOME TAX"]
            pan_number = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', extracted_text)
            if any(fuzzy_match(extracted_text, k) for k in pan_keywords) and pan_number:
                status = "Verified as PAN Card"
            else:
                status = "Invalid document for PAN Card"

        # Driving License
        elif doc_type == 'driving_license':
            dl_keywords = ["DRIVING LICENCE", "DRIVING LICENSE", "TRANSPORT", "MOTOR VEHICLES", "UNION OF INDIA"]
            # Use regex that allows optional space between state code and numbers
            dl_number = re.search(r'\b[A-Z]{2}[0-9]{2}\s?[0-9]{11}\b', extracted_text)
            
            if any(fuzzy_match(extracted_text, k) for k in dl_keywords) and dl_number:
                status = "Verified as Driving License"
            else:
                status = "Invalid document for Driving License"

        # Voter ID
        elif doc_type == 'voter_id':
            voter_keywords = ["ELECTION COMMISSION", "VOTER", "PHOTO IDENTITY CARD", "ELECTOR"]
            epic_number = re.search(r'\b[A-Z]{3}[0-9]{7}\b', extracted_text)
            if any(fuzzy_match(extracted_text, k) for k in voter_keywords) and epic_number:
                status = "Verified as Voter ID"
            else:
                status = "Invalid document for Voter ID"

        # Passport
        elif doc_type == 'passport':
            # passport_keywords = ["PASSPORT", "REPUBLIC OF INDIA", "MINISTRY OF EXTERNAL AFFAIRS"]
            # Match passport number (starts with a letter followed by 7 digits)
            passport_number_match = re.search(r'\b([A-Z][0-9]{7})\b', extracted_text)
            
            # Try MRZ zone format detection (optional but strong signal)
            mrz_match = re.search(r'[A-Z0-9<]{30,}', extracted_text)
            
            # Fuzzy keyword match + number or MRZ detected
            if passport_number_match or mrz_match:
                status = "Verified as Passport"
            else:
                status = "Invalid document for Passport"

        print(f"\n✅ Verification Status: {status}")
        print(f"\n📄 Extracted Text:\n{extracted_text}")
        return status, extracted_text

    except Exception as e:
        print(f"[ERROR] Document verification failed: {str(e)}")
        return "Rejected", str(e)
