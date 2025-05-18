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

def extract_aadhaar_name(text):
    """Extract name from Aadhaar card text format."""
    # Split text into lines and clean them
    lines = [line.strip() for line in text.upper().split('\n') if line.strip()]
    
    for i, line in enumerate(lines):
        # Look for lines that come right before DOB
        if i + 1 < len(lines) and "DOB:" in lines[i + 1]:
            # This line is likely the English name
            # Remove any common prefixes/suffixes
            name = line.strip()
            # Clean up any extra spaces
            name = ' '.join(word for word in name.split() if not any(x in word for x in ["DOB:", "/DOB", "MALE", "FEMALE"]))
            if len(name.split()) >= 2:  # Ensure we have at least two parts in the name
                return name
            
        # Alternative method: Look for lines with multiple words between Government of India and DOB
        if "GOVERNMENT OF INDIA" in line or "UNIQUE IDENTIFICATION" in line:
            # Check next few lines for name
            for j in range(i+1, min(i+4, len(lines))):
                if "DOB:" in lines[j]:
                    break
                potential_name = lines[j].strip()
                # Skip lines with common Aadhaar card text
                if any(x in potential_name for x in ["GOVERNMENT", "UNIQUE", "ADDRESS:", "AADHAAR", "MALE", "FEMALE", "DOB:"]):
                    continue
                if len(potential_name.split()) >= 2:
                    return potential_name
    
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
    """Extract voter ID number and name from the text."""
    details = {
        'voter_id': None,
        'name': None
    }
    
    # Split text into lines and clean them
    lines = [line.strip() for line in text.upper().split('\n') if line.strip()]
    
    # Look for voter ID number (e.g., GDNO225185 format)
    # Pattern: 3 letters + 1 letter/number + 6 numbers
    voter_id_pattern = re.compile(r'\b[A-Z]{3}[A-Z0-9]\d{6}\b')
    
    # Look for name after "ELECTOR'S NAME :" or similar patterns
    name_patterns = [
        r"ELECTOR'S NAME\s*[:.-]\s*(.*?)(?:\s*\n|$)",
        r"ELECTOR'S NAME\s*[:-]\s*(.*?)(?:\s*\n|$)",
        r"ELECTOR NAME\s*[:.-]\s*(.*?)(?:\s*\n|$)",
        r"ELECTOR.*NAME.*[:.-]\s*(.*?)(?:\s*\n|$)"  # More flexible pattern
    ]
    
    # Search in each line
    for line in lines:
        # Search for voter ID
        if not details['voter_id']:
            voter_match = voter_id_pattern.search(line)
            if voter_match:
                # Clean the voter ID by removing spaces and special characters
                voter_id = clean_voter_id(voter_match.group(0))
                if len(voter_id) == 10:  # Must be exactly 10 characters
                    details['voter_id'] = voter_id
                    print(f"Found voter ID match: {voter_id}")
                    print(f"  First 3 letters: {voter_id[:3]}")
                    print(f"  Fourth character (letter/number): {voter_id[3]}")
                    print(f"  Last 6 digits: {voter_id[4:]}")
        
        # Search for name
        if not details['name']:
            for pattern in name_patterns:
                name_match = re.search(pattern, line, re.IGNORECASE)
                if name_match:
                    # Clean the name by removing special characters but keep spaces
                    name = re.sub(r'[^A-Z\s]', '', name_match.group(1).upper()).strip()
                    if len(name.split()) >= 2:  # Ensure we have at least two parts in the name
                        details['name'] = name
                        break
    
    # Debug output
    print(f"Extracted Voter ID: {details['voter_id']}")
    print(f"Extracted Name: {details['name']}")
    
    return details

def extract_pan_name(text):
    """Extract name from PAN card text format."""
    print("[PAN DEBUG] Starting name extraction")
    print("[PAN DEBUG] Input text:")
    print(text)
    
    # Split text into lines and clean them
    lines = [line.strip() for line in text.upper().split('\n') if line.strip()]
    print(f"[PAN DEBUG] Found {len(lines)} non-empty lines")
    
    # Common patterns found in PAN cards
    name_patterns = [
        r"NAME\s*[:.-]*\s*([A-Z\s]+?)(?:\s*(?:FATHER|LAST|SURNAME|DOB|DATE|/|\n|$))",
        r"\bNAME\b[:\s.-]*([A-Z\s]+?)(?:\s*(?:FATHER|LAST|SURNAME|DOB|DATE|/|\n|$))",
        r"(?<=\bNAME\b)[\s:.-]*([A-Z\s]+?)(?:\s*(?:FATHER|LAST|SURNAME|DOB|DATE|/|\n|$))",
        r"INCOME\s*TAX\s*DEPARTMENT.*?\n(.*?)(?:\s*(?:FATHER|LAST|SURNAME|DOB|DATE|/|\n|$))",
        r"GOVT.\s*OF\s*INDIA.*?\n(.*?)(?:\s*(?:FATHER|LAST|SURNAME|DOB|DATE|/|\n|$))"
    ]
    
    # First try pattern matching
    print("[PAN DEBUG] Trying pattern matching...")
    for line in lines:
        print(f"[PAN DEBUG] Checking line: {line}")
        for i, pattern in enumerate(name_patterns):
            print(f"[PAN DEBUG] Trying pattern {i+1}")
            name_match = re.search(pattern, line, re.DOTALL)
            if name_match:
                name = name_match.group(1).strip()
                print(f"[PAN DEBUG] Found potential name with pattern {i+1}: {name}")
                # Clean the name
                name = re.sub(r'[^A-Z\s]', '', name)
                name = ' '.join(word for word in name.split() if len(word) > 1)  # Remove single characters
                if len(name.split()) >= 2:  # Ensure we have at least two parts in the name
                    print(f"[PAN DEBUG] Valid name found: {name}")
                    return name
                else:
                    print("[PAN DEBUG] Name too short, continuing search...")
    
    # If no pattern matched, try positional logic
    print("[PAN DEBUG] Pattern matching failed, trying positional logic...")
    for i, line in enumerate(lines):
        # Look for common PAN card headers
        if any(header in line for header in ["INCOME TAX DEPARTMENT", "GOVT. OF INDIA", "PERMANENT ACCOUNT NUMBER"]):
            print(f"[PAN DEBUG] Found header in line {i+1}: {line}")
            # Check next few lines for potential name
            for j in range(i+1, min(i+4, len(lines))):
                potential_name = lines[j].strip()
                print(f"[PAN DEBUG] Checking line {j+1} for name: {potential_name}")
                # Skip lines with common PAN card text
                if any(x in potential_name for x in ["PERMANENT", "ACCOUNT", "NUMBER", "FATHER", "DATE", "SIGNATURE", "PAN", "GOVT", "INCOME"]):
                    print(f"[PAN DEBUG] Line {j+1} contains common text, skipping")
                    continue
                # Clean the potential name
                potential_name = re.sub(r'[^A-Z\s]', '', potential_name)
                potential_name = ' '.join(word for word in potential_name.split() if len(word) > 1)
                if len(potential_name.split()) >= 2:
                    print(f"[PAN DEBUG] Valid name found using positional logic: {potential_name}")
                    return potential_name
                else:
                    print("[PAN DEBUG] Name too short, continuing search...")
    
    # If still no name found, try looking for text between PAN number and Father's name
    print("[PAN DEBUG] Positional logic failed, trying PAN number to Father's name method...")
    pan_pattern = r'\b[A-Z]{5}[0-9]{4}[A-Z]\b'
    father_pattern = r'FATHER|FATHER\'S NAME|FATHER NAME'
    
    for i, line in enumerate(lines):
        if re.search(pan_pattern, line):
            print(f"[PAN DEBUG] Found PAN number in line {i+1}: {line}")
            # Look at lines between PAN number and Father's name
            for j in range(i+1, len(lines)):
                if re.search(father_pattern, lines[j]):
                    print(f"[PAN DEBUG] Found Father's name line at {j+1}")
                    break
                potential_name = lines[j].strip()
                print(f"[PAN DEBUG] Checking line {j+1} for name: {potential_name}")
                # Clean and validate the potential name
                potential_name = re.sub(r'[^A-Z\s]', '', potential_name)
                potential_name = ' '.join(word for word in potential_name.split() if len(word) > 1)
                if len(potential_name.split()) >= 2:
                    print(f"[PAN DEBUG] Valid name found between PAN and Father's name: {potential_name}")
                    return potential_name
                else:
                    print("[PAN DEBUG] Name too short, continuing search...")
    
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
            
            # If name was extracted, verify it
            if details['name']:
                print(f"Extracted Name: {details['name']}")
                # Clean both names for comparison
                doc_name = clean_text(details['name'])
                db_name = clean_text(record.name)
                print(f"Comparing names: '{doc_name}' with '{db_name}'")
                
                name_similarity = SequenceMatcher(None, doc_name, db_name).ratio()
                print(f"Name similarity: {name_similarity}")
                
                if name_similarity >= 0.8:  # 80% similarity threshold
                    return "Verified", f"Voter ID verified successfully. Matched record for {details['name']}"
                else:
                    return "Rejected", "Name in document does not match records"
            
            return "Verified", "Voter ID verified successfully"

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
                
            # Verify document type
            if record.document_type != 'passport':
                return "Rejected", "Document type mismatch"
                
            return "Verified", "Passport verified successfully"

        return status, "Invalid document type"

    except Exception as e:
        print(f"[ERROR] Document verification failed: {str(e)}")
        return "Rejected", str(e)
