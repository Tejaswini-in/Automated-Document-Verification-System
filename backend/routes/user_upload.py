from flask import Blueprint, request, jsonify, session, send_from_directory
from werkzeug.utils import secure_filename
from database import db
from models.document import Document
from datetime import datetime
import os

user_upload = Blueprint('user_upload', __name__)

UPLOAD_FOLDER = "uploads"  # Make sure this folder exists
ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}

def allowed_file(filename):
    return '.' in filename and '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 🆕 Check if user is logged in using session
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

# Fetch user documents
@user_upload.route("/api/user/documents", methods=["GET"])
@login_required
def get_user_documents():
    try:
        user_id = session.get("user_id")

        documents = Document.query.filter_by(user_id=user_id).all()

        result = []
        for doc in documents:
            result.append({
                "id": doc.id,
                "type": doc.doc_type,
                "name": os.path.basename(doc.file_path),
                "file_url": f"/uploads/{os.path.basename(doc.file_path)}",
                "status": doc.status,
                "verified_by": doc.verified_by or "Pending",
                "uploaded_at": doc.uploaded_at.strftime("%Y-%m-%d %H:%M:%S") if doc.uploaded_at else "N/A"
            })

        return jsonify({"documents": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Delete user document
@user_upload.route("/api/user/documents/<int:doc_id>", methods=["DELETE"])
@login_required
def delete_user_document(doc_id):
    try:
        user_id = session.get("user_id")

        document = Document.query.filter_by(id=doc_id, user_id=user_id).first()

        if not document:
            return jsonify({"error": "Document not found."}), 404

        # Delete the file if exists
        if os.path.exists(document.file_path):
            os.remove(document.file_path)

        db.session.delete(document)
        db.session.commit()

        return jsonify({"message": "Document deleted successfully."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Upload a new document
@user_upload.route("/api/user/upload", methods=["POST"])
@login_required
def upload_user_document():
    try:
        user_id = session.get("user_id")

        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']
        doc_type = request.form.get('doc_type')

        if not file or file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400

        if not doc_type:
            return jsonify({"error": "Document type is required"}), 400

        # Save file securely
        filename = secure_filename(file.filename)
        upload_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(upload_path)

        # Save in database
        new_document = Document(
            user_id=user_id,
            doc_type=doc_type,
            file_path=upload_path,
            status="Pending",
            result_data="",
            uploaded_at=datetime.utcnow(),
            verified_by=None
        )
        db.session.add(new_document)
        db.session.commit()

        return jsonify({"message": "Document uploaded successfully."}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
