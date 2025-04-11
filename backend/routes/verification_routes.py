import os
import uuid
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from database import db
from models.document import Document
from services.ocr_service import extract_text
from services.validate_document import validate_document


verify_bp = Blueprint('verify', __name__)

@verify_bp.route('/upload', methods=['POST'])
def upload_document():
    try:
        print("[STEP 1] Receiving file and doc_type...")

        file = request.files.get('file')
        doc_type = request.form.get('doc_type')

        if not file:
            raise Exception("No file uploaded.")
        if not doc_type:
            raise Exception("Document type is missing.")

        print("[DEBUG] File received:", file.filename)
        print("[DEBUG] Document type:", doc_type)

        # Ensure uploads directory exists
        os.makedirs('uploads', exist_ok=True)

        # Save with unique filename to prevent overwrites
        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        path = os.path.join('uploads', filename)
        file.save(path)

        print(f"[STEP 2] File saved to: {path}")
        print("[STEP 3] Starting OCR...")

        extracted_text = extract_text(path)

        print(f"[STEP 4] OCR Result:\n{extracted_text}")

        # Handle OCR failure
        if extracted_text.startswith("ERROR:"):
            status = "Rejected"
        else:
            status = "Verified" if len(extracted_text.strip()) > 20 else "Rejected"

        print(f"[STEP 5] Status: {status}")
        print("[STEP 6] Saving to database...")

        doc = Document(
            user_id=1,  # Replace with session-based ID if available
            doc_type=doc_type,
            file_path=path,
            status=status,
            result_data=extracted_text
        )
        db.session.add(doc)
        db.session.commit()

        print("[STEP 7] Done. Sending response.")
        return jsonify({'status': status, 'extracted': extracted_text})

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print("[ERROR] Upload exception occurred:\n", error_trace)
        return jsonify({'status': 'error', 'message': str(e), 'trace': error_trace}), 500