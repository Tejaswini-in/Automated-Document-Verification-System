import json
import os

from flask import Blueprint, jsonify, request
from models.user import User
from models.document import Document
from models.audit_log import AuditLog
from models.data import Data
from database import db

admin_bp = Blueprint('admin', __name__)

# ------------------- UTILITY: Add Audit Entry ------------------- #
def log_action(user_id, action):
    log = AuditLog(user_id=user_id, action=action)
    db.session.add(log)
    db.session.commit()

# ------------------- Verification Data Management ------------------- #
@admin_bp.route('/verification-data', methods=['GET'])
def get_verification_data():
    data = Data.query.all()
    return jsonify([{
        'id': record.id,
        'name': record.name,
        'id_number': record.id_number,
        'document_type': record.document_type,
        'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'updated_at': record.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    } for record in data])

@admin_bp.route('/verification-data', methods=['POST'])
def add_verification_data():
    try:
        data = request.json
        
        # Check if record with this ID already exists
        existing_record = Data.query.filter_by(id_number=data['id_number']).first()
        
        if existing_record:
            # Update existing record
            existing_record.name = data['name']
            existing_record.document_type = data['document_type']
            action = f"Updated verification data for {data['name']}"
            message = "Verification data updated successfully"
        else:
            # Create new record
            new_record = Data(
                name=data['name'],
                id_number=data['id_number'],
                document_type=data['document_type'],
                keywords=''  # Default empty string for keywords
            )
            db.session.add(new_record)
            action = f"Added verification data for {data['name']}"
            message = "Verification data added successfully"
            
        db.session.commit()
        log_action(user_id=1, action=action)
        return jsonify({'message': message})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/verification-data/<int:id>', methods=['PUT'])
def update_verification_data(id):
    try:
        record = Data.query.get_or_404(id)
        data = request.json
        record.name = data.get('name', record.name)
        record.id_number = data.get('id_number', record.id_number)
        record.document_type = data.get('document_type', record.document_type)
        db.session.commit()
        log_action(user_id=1, action=f"Updated verification data for {record.name}")
        return jsonify({'message': 'Verification data updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/verification-data/<int:id>', methods=['DELETE'])
def delete_verification_data(id):
    try:
        record = Data.query.get_or_404(id)
        db.session.delete(record)
        db.session.commit()
        log_action(user_id=1, action=f"Deleted verification data for {record.name}")
        return jsonify({'message': 'Verification data deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# ------------------- 1. Manage Users ------------------- #
@admin_bp.route('/users', methods=['GET'])
def get_all_users():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    query = User.query.paginate(page=page, per_page=limit, error_out=False)
    users = query.items

    log_action(user_id=1, action="Manage Users Access")  # Replace with real admin ID
    return jsonify({
        "users": [
            {
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "role": u.role
            } for u in users
        ],
        "total": query.total,
        "page": query.page,
        "pages": query.pages
    })

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    log_action(user_id, f"Deleted user {user.email}")
    return jsonify({"message": "User deleted successfully"})

# ------------------- 2. View Documents ------------------- #
@admin_bp.route('/documents', methods=['GET'])
def get_all_documents():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    status = request.args.get('status', None)

    query = Document.query
    if status:
        query = query.filter(Document.status == status)

    paginated = query.paginate(page=page, per_page=limit, error_out=False)
    docs = paginated.items

    log_action(user_id=1, action="View Documents Access")
    return jsonify({
        "documents": [
            {
                "id": d.id,
                "user_id": d.user_id,
                "type": d.doc_type,
                "status": d.status,
                "result": d.result_data,
                "uploaded_at": d.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
            } for d in docs
        ],
        "total": paginated.total,
        "page": paginated.page,
        "pages": paginated.pages
    })

@admin_bp.route('/documents/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    doc = Document.query.get(doc_id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    db.session.delete(doc)
    db.session.commit()
    log_action(doc.user_id, f"Deleted document {doc.id}")
    return jsonify({"message": "Document deleted successfully"})

# ------------------- 3. AI Forgery Reports ------------------- #
@admin_bp.route('/reports', methods=['GET'])
def get_reports():
    reports = Document.query.filter(Document.result_data != None).all()
    log_action(user_id=1, action="Forgery Reports Access")
    return jsonify([
        {
            "id": r.id,
            "user_id": r.user_id,
            "type": r.doc_type,
            "status": r.status,
            "result": r.result_data
        } for r in reports
    ])

# ------------------- 4. Audit Logs ------------------- #
@admin_bp.route('/audit-logs', methods=['GET'])
def get_audit_logs():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
    log_action(user_id=1, action="Audit Logs Access")
    return jsonify([
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "timestamp": log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for log in logs
    ])
