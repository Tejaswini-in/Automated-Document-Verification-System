import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import re
from difflib import SequenceMatcher
import cv2
import numpy as np
from models.data import Data
from database import db

from services.ocr_service import extract_text_from_image

def clean_text(text):
    """Remove non-alphabetic characters, normalize whitespace, and convert to lower case."""
    text = re.sub(r'[^a-zA-Z\s]', '', text).lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text

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

def extract_aadhaar_name(text):
    lines = [line.strip() for line in text.upper().split('\n') if line.strip()]
    for i, line in enumerate(lines):
        # Look for line with "DOB" and take the previous line as name
        if "DOB" in line and i > 0:
            possible_name = lines[i-1].strip()
            # Filter out lines that are not likely names
            if all(x not in possible_name for x in ["GOVERNMENT", "UNIQUE", "INDIA", "DOB", "FEMALE", "MALE", "YEAR", "BIRTH", "ADDRESS", "ENROLMENT", "AADHAAR", "AUTHORITY"]):
                if len(possible_name.split()) >= 2:
                    return possible_name.title()
    # Fallback: look for the first line with at least two words and not a keyword
    for line in lines:
        if len(line.split()) >= 2 and all(x not in line for x in ["GOVERNMENT", "UNIQUE", "INDIA", "DOB", "FEMALE", "MALE", "YEAR", "BIRTH", "ADDRESS", "ENROLMENT", "AADHAAR", "AUTHORITY"]):
            return line.title()
    return None

def clean_voter_id(text):
    """Clean voter ID by removing spaces and special characters."""
    # Remove spaces and special characters
    cleaned = re.sub(r'[^A-Z0-9]', '', text.upper())
    return cleaned

def test_voter_id_pattern(voter_id):
    """Test if a voter ID matches the expected pattern."""
    # Pattern: 3 letters + 1 letter/number + 6 numbers
    pattern = re.compile(r'\b[A-Z]{3}[A-Z0-9]\d{6}\b')
    match = pattern.match(voter_id)
    if match:
        return True, match.group(0)
    return False, None

def extract_voter_id_details(text):
    print("Full OCR output for Voter ID:", text)
    details = {'voter_id': None, 'name': None}
    lines = [line.strip() for line in text.upper().split('\n') if line.strip()]
    joined = ''.join(lines)
    cleaned = re.sub(r'[^A-Z0-9]', '', joined)
    skip_words = {"ELECTIONCO", "COMMISSIONO", "INDIAELECT", "PHOTOIDENT", "CARD"}

    # Fuzzy match any 9-11 character substring to a database ID
    db_ids = [r.id_number for r in Data.query.filter_by(document_type='voter_id').all()]
    best_match = None
    best_score = 0
    for i in range(len(cleaned) - 8):
        for length in [9, 10, 11]:
            candidate = cleaned[i:i+length]
            if candidate.isalnum() and candidate not in skip_words:
                for db_id in db_ids:
                    score = SequenceMatcher(None, candidate, db_id).ratio()
                    if score > best_score:
                        best_score = score
                        best_match = db_id
    if best_score > 0.8:
        details['voter_id'] = best_match
        print(f"Fuzzy matched voter ID: {best_match} (score: {best_score})")
    # Name extraction (same as before)
    for i, line in enumerate(lines):
        if "ELECTOR'S NAME" in line or "NAME" in line:
            if ':' in line:
                possible_name = line.split(':', 1)[1].strip()
                possible_name_clean = re.sub(r'[^A-Z\s]', '', possible_name)
                if len(possible_name_clean.split()) >= 2 and all(w.isalpha() for w in possible_name_clean.split()):
                    details['name'] = possible_name_clean
                    break
            if i+1 < len(lines):
                next_line = lines[i+1].strip()
                next_line_clean = re.sub(r'[^A-Z\s]', '', next_line)
                if len(next_line_clean.split()) >= 2 and all(w.isalpha() for w in next_line_clean.split()):
                    details['name'] = next_line_clean
                    break
    print(f"Extracted Voter ID: {details['voter_id']}")
    print(f"Extracted Name: {details['name']}")
    return details

def extract_pan_name(text):
    print("[PAN DEBUG] Starting name extraction")
    print("[PAN DEBUG] Input text:")
    print(text)
    lines = [line.strip() for line in text.upper().split('\n') if line.strip()]
    print(f"[PAN DEBUG] Found {len(lines)} non-empty lines")

    skip_keywords = [
        "PERMANENT", "ACCOUNT", "NUMBER", "FATHER", "DATE", "SIGNATURE", "PAN", "GOVT", "INCOME",
        "STREE", "TANT", "EQUAL", "PHOTO", "GENDER", "MALE", "FEMALE", "YEAR", "BIRTH"
    ]

    # 1. Look for 'NAME' label and take the next non-empty line, but stop if 'FATHER' label is encountered
    for i, line in enumerate(lines):
        if "NAME" in line and "FATHER" not in line and i + 1 < len(lines):
            # Find the next non-empty line that is not a label
            for j in range(i + 1, len(lines)):
                possible_name = lines[j].strip()
                if "FATHER" in possible_name or "SURNAME" in possible_name or "DOB" in possible_name:
                    break  # Stop if we hit the father's name label or other labels
                if all(x not in possible_name for x in skip_keywords) and len(possible_name.split()) >= 2:
                    print(f"[PAN DEBUG] Found name under 'NAME' label: {possible_name}")
                    return possible_name.title()
            break  # Only process the first 'NAME' label

    # 2. Try to find the first line after "INCOME TAX DEPARTMENT" or "GOVT. OF INDIA" that looks like a name (old format)
    for i, line in enumerate(lines):
        if "INCOME TAX DEPARTMENT" in line or "GOVT. OF INDIA" in line:
            for j in range(i+1, min(i+4, len(lines))):
                possible_name = lines[j].strip()
                print(f"[PAN DEBUG] Candidate after header: {possible_name}")
                if any(x in possible_name for x in skip_keywords):
                    continue
                words = possible_name.split()
                if len(words) >= 2 and sum(w.isalpha() for w in words) >= len(words) - 1:
                    print(f"[PAN DEBUG] Found name after header: {possible_name}")
                    return possible_name.title()

    # 3. Fallback: pattern matching logic
    name_patterns = [
        r"NAME\s*[:.-]*\s*([A-Z\s]+?)(?:\s*(?:FATHER|LAST|SURNAME|DOB|DATE|/|\n|$))",
        r"\bNAME\b[:\s.-]*([A-Z\s]+?)(?:\s*(?:FATHER|LAST|SURNAME|DOB|DATE|/|\n|$))",
        r"(?<=\bNAME\b)[\s:.-]*([A-Z\s]+?)(?:\s*(?:FATHER|LAST|SURNAME|DOB|DATE|/|\n|$))",
        r"INCOME\s*TAX\s*DEPARTMENT.*?\n(.*?)(?:\s*(?:FATHER|LAST|SURNAME|DOB|DATE|/|\n|$))",
        r"GOVT.\s*OF\s*INDIA.*?\n(.*?)(?:\s*(?:FATHER|LAST|SURNAME|DOB|DATE|/|\n|$))"
    ]
    for line in lines:
        for pattern in name_patterns:
            name_match = re.search(pattern, line, re.DOTALL)
            if name_match:
                name = name_match.group(1).strip()
                name = re.sub(r'[^A-Z\s]', '', name)
                name = ' '.join(word for word in name.split() if len(word) > 1)
                if len(name.split()) >= 2:
                    print(f"[PAN DEBUG] Valid name found: {name}")
                    return name.title()

    # 4. Fallback: first line with at least two words after PAN number
    pan_pattern = r'\b[A-Z]{5}[0-9]{4}[A-Z]\b'
    for i, line in enumerate(lines):
        if re.search(pan_pattern, line):
            for j in range(i+1, min(i+4, len(lines))):
                possible_name = lines[j].strip()
                if len(possible_name.split()) >= 2 and all(x not in possible_name for x in skip_keywords):
                    print(f"[PAN DEBUG] Fallback name after PAN number: {possible_name}")
                    return possible_name.title()
    print("[PAN DEBUG] All name extraction methods failed")
    return None

def verify_document(doc_path, doc_type):
    try:
        # Extract text using OCR
        text = extract_text_from_image(doc_path)
        extracted_text = text.upper()
        print(f"Extracted Text: {extracted_text}")
        status = "Rejected"
        
        # Aadhaar
        if doc_type == 'aadhaar':
            # First try to find the Aadhaar number
            aadhaar_match = re.search(r'\b\d{4}\s\d{4}\s\d{4}\b', extracted_text)
            if not aadhaar_match:
                return "Rejected", "Could not find valid Aadhaar number in document"
                
            aadhaar_number = aadhaar_match.group(0)
            print(f"Found Aadhaar Number: {aadhaar_number}")
            
            # Check if this ID exists in database
            record = Data.query.filter_by(id_number=aadhaar_number).first()
            if not record:
                return "Rejected", "No matching Aadhaar record found in database"
                
            # Verify document type
            if record.document_type != 'aadhaar':
                return "Rejected", "Document type mismatch"
                
            # Now extract and verify name
            name = extract_aadhaar_name(extracted_text)
            if not name:
                return "Rejected", "Could not extract name from document"
                
            print(f"Extracted Name: {name}")
            
            # Compare names using fuzzy matching
            name_similarity = SequenceMatcher(None, 
                                        clean_text(name), 
                                        clean_text(record.name)).ratio()
            
            print(f"Extracted Name (raw): '{name}'")
            print(f"Database Name (raw): '{record.name}'")
            print(f"Extracted Name (clean): '{clean_text(name)}'")
            print(f"Database Name (clean): '{clean_text(record.name)}'")
            print(f"Name similarity: {name_similarity}")
            
            if name_similarity >= 0.8:  # 80% similarity threshold
                status = "Verified"
                return status, f"Document verified successfully. Matched record for {name}"
            else:
                return "Rejected", "Name in document does not match records"

        # PAN
        elif doc_type == 'pan':
            # First try to find PAN number
            pan_match = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', extracted_text)
            if not pan_match:
                return "Rejected", "Could not find valid PAN number in document"
                
            pan_number = pan_match.group(0)
            print(f"Found PAN Number: {pan_number}")
            
            # Extract name from PAN card
            name = extract_pan_name(extracted_text)
            if not name:
                print("Could not extract name from PAN card")
                return "Rejected", "Could not extract name from document"
            
            print(f"Extracted Name: {name}")
            
            # Check if this ID exists in database
            record = Data.query.filter_by(id_number=pan_number).first()
            if not record:
                return "Rejected", "No matching PAN record found in database"
                
            # Verify document type
            if record.document_type != 'pan':
                return "Rejected", "Document type mismatch"
            
            # Compare names using fuzzy matching
            doc_name = clean_text(name)
            db_name = clean_text(record.name)
            print(f"Comparing names: '{doc_name}' with '{db_name}'")
            
            name_similarity = SequenceMatcher(None, doc_name, db_name).ratio()
            print(f"Name similarity: {name_similarity}")
            
            print(f"Extracted Name (raw): '{name}'")
            print(f"Database Name (raw): '{record.name}'")
            print(f"Extracted Name (clean): '{clean_text(name)}'")
            print(f"Database Name (clean): '{clean_text(record.name)}'")
            print(f"Name similarity: {name_similarity}")
            
            if name_similarity >= 0.8:  # 80% similarity threshold
                return "Verified", f"PAN Card verified successfully. Matched record for {name}"
            else:
                return "Rejected", "Name in document does not match records"

        # Driving License
        elif doc_type == 'driving_license':
            # First try to find DL number
            dl_match = re.search(r'\b[A-Z]{2}[0-9]{2}\s?[0-9]{11}\b', extracted_text)
            if not dl_match:
                return "Rejected", "Could not find valid Driving License number in document"
                
            dl_number = dl_match.group(0)
            print(f"Found DL Number: {dl_number}")
            
            # Check if this ID exists in database
            record = Data.query.filter_by(id_number=dl_number).first()
            if not record:
                return "Rejected", "No matching Driving License record found in database"
                
            # Verify document type
            if record.document_type != 'driving_license':
                return "Rejected", "Document type mismatch"
                
            return "Verified", "Driving License verified successfully"

        # Voter ID
        elif doc_type == 'voter_id':
            # Extract voter ID details
            details = extract_voter_id_details(extracted_text)
            if not details['voter_id']:
                print("Failed to extract voter ID. Full text:", extracted_text)
                return "Rejected", "Could not find valid Voter ID number in document"
            voter_number = details['voter_id']
            print(f"Found Voter ID Number: {voter_number}")
            # Check if this ID exists in database
            record = Data.query.filter_by(id_number=voter_number).first()
            if not record:
                return "Rejected", "No matching Voter ID record found in database"
            # Verify document type
            if record.document_type != 'voter_id':
                return "Rejected", "Document type mismatch"
            # Require name extraction and matching
            if not details['name']:
                return "Rejected", "Could not extract name from document"
            print(f"Extracted Name: {details['name']}")
            doc_name = clean_text(details['name'])
            db_name = clean_text(record.name)
            print(f"Comparing names: '{doc_name}' with '{db_name}'")
            name_similarity = SequenceMatcher(None, doc_name, db_name).ratio()
            print(f"Name similarity: {name_similarity}")
            if name_similarity >= 0.8:
                return "Verified", f"Voter ID verified successfully. Matched record for {details['name']}"
            else:
                return "Rejected", "Name in document does not match records"

        # Passport
        elif doc_type == 'passport':
            # First try to find Passport number
            passport_match = re.search(r'\b([A-Z][0-9]{7})\b', extracted_text)
            if not passport_match:
                # Check for MRZ as fallback
                mrz_match = re.search(r'[A-Z0-9<]{30,}', extracted_text)
                if not mrz_match:
                    return "Rejected", "Could not find valid Passport number in document"
                return "Verified", "Passport format verified (MRZ found)"
            passport_number = passport_match.group(0)
            print(f"Found Passport Number: {passport_number}")
            # Check if this ID exists in database
            record = Data.query.filter_by(id_number=passport_number).first()
            if not record:
                return "Rejected", "No matching Passport record found in database"
            # Verify document type (case-insensitive)
            if record.document_type.strip().lower() != 'passport':
                return "Rejected", "Document type mismatch"
            return "Verified", "Passport verified successfully"

        return status, "Invalid document type"

    except Exception as e:
        print(f"[ERROR] Document verification failed: {str(e)}")
        return "Rejected", str(e)

print(SequenceMatcher(None, "meena devi", "meena davi").ratio())
