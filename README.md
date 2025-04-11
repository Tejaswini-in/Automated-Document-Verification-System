# Automated Document Verification System

This project verifies documents like Aadhaar, PAN, and Passport using OCR and AI models.

## Features

- User/Admin login & registration
- Upload documents
- Text extraction using OCR
- Status: Verified / Rejected
- Admin dashboard for reports

## Tech Stack

- 🧠 Backend: Python Flask
- 💻 Frontend: React with Bootstrap
- 🧾 OCR: PyTesseract
- 🧠 AI Logic: Placeholder in Flask for document verification

## Setup Instructions

### 🔧 Backend (Python)

```bash
cd automated-document-verification/backend
python -m venv venv
source venv/bin/activate   # On Windows: venv\\Scripts\\activate
pip install -r ../../requirements.txt
python app.py
