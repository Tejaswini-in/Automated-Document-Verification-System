import json
import os
from flask import Blueprint, jsonify, request
from models.user import User
from models.document import Document
from models.audit_log import AuditLog
from database import db

admin_bp = Blueprint('admin', __name__)

# ------------------- UTILITY: Add Audit Entry ------------------- #
def log_action(user_id, action):
    log = AuditLog(user_id=user_id, action=action)
    db.session.add(log)
    db.session.commit()

# ------------------- 1. Manage Users ------------------- #
@admin_bp.route('/users', methods=['GET'])
def get_all_users():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    query = User.query.paginate(page=page, per_page=limit, error_out=False)
    users = query.items

    log_action(user_id=1, action="Accessed Manage Users")

    return jsonify({
        "users": [
            {
                "id": u.id,
                "username": u.name,
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

    log_action(user_id=1, action="Accessed View Documents")

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
    log_action(user_id=1, action="Accessed Forgery Reports")
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
    log_action(user_id=1, action="Accessed Audit Logs")
    return jsonify([
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "timestamp": log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for log in logs
    ])
