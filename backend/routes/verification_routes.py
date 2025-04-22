import os
import uuid
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from database import db
from models.document import Document
from services.ocr_service import extract_text

verify_bp = Blueprint('verify', __name__)

# File upload route for document verification
@verify_bp.route('/upload', methods=['POST'])
def upload_document():
    try:
        print("[STEP 1] Receiving file and doc_type...")

        # Extract the file and doc_type from the request
        file = request.files.get('file')
        doc_type = request.form.get('doc_type')

        # Validate if the file and document type are present
        if not file:
            raise Exception("No file uploaded.")
        if not doc_type:
            raise Exception("Document type is missing.")

        print(f"[DEBUG] File received: {file.filename}")
        print(f"[DEBUG] Document type: {doc_type}")

        # Ensure the 'uploads' directory exists
        os.makedirs('uploads', exist_ok=True)

        # Create a unique filename to prevent overwriting
        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        file_path = os.path.join('uploads', filename)
        
        # Save the uploaded file
        file.save(file_path)

        print(f"[STEP 2] File saved to: {file_path}")
        print("[STEP 3] Starting OCR...")

        # Extract text from the uploaded file using OCR
        extracted_text = extract_text(file_path)

        print(f"[STEP 4] OCR Result:\n{extracted_text}")

        # Handle OCR failure
        if extracted_text.startswith("ERROR:"):
            status = "Rejected"
        else:
            status = "Verified" if len(extracted_text.strip()) > 20 else "Rejected"

        print(f"[STEP 5] Status: {status}")

        # Save document details to the database
        print("[STEP 6] Saving to database...")

        doc = Document(
            user_id=1,  # Replace with the actual session-based user ID
            doc_type=doc_type,
            file_path=file_path,
            status=status,
            result_data=extracted_text
        )
        
        # Add the document record to the database session and commit
        db.session.add(doc)
        db.session.commit()

        print("[STEP 7] Document successfully saved. Sending response.")

        # Return the verification result and extracted text in the response
        return jsonify({
            'status': status,
            'extracted': extracted_text
        })

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        
        # Log the error trace
        print("[ERROR] Upload exception occurred:\n", error_trace)
        
        # Return a detailed error response
        return jsonify({
            'status': 'error',
            'message': str(e),
            'trace': error_trace
        }), 500
