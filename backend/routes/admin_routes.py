from flask import Blueprint, jsonify
from models.document import Document

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/reports', methods=['GET'])
def reports():
    docs = Document.query.all()
    return jsonify([
        {
            "id": d.id,
            "type": d.doc_type,
            "status": d.status,
            "result": d.result_data
        } for d in docs
    ])
