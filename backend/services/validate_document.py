import re

def is_valid_aadhaar(text):
    return bool(re.search(r"\b\d{4}\s\d{4}\s\d{4}\b", text))

def is_valid_pan(text):
    return bool(re.search(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", text))

def is_valid_government_id(text):
    keywords = [
        "Government of India",
        "Election Commission",
        "Passport",
        "Driving License",
        "Ministry",
        "Identity Card"
    ]
    for keyword in keywords:
        if keyword.lower() in text.lower():
            return True
    return False

def validate_document(text, doc_type):
    doc_type = doc_type.lower()
    if doc_type == "aadhaar":
        return is_valid_aadhaar(text)
    elif doc_type == "pan":
        return is_valid_pan(text)
    elif doc_type in ["voter", "passport", "dl", "govt", "government", "other"]:
        return is_valid_government_id(text)
    else:
        return len(text.strip()) > 20
