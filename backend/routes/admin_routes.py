from flask import Blueprint, jsonify, request, session
from models.user import User
from models.document import Document
from models.audit_log import AuditLog
from database import db
from utils.auth_decorators import admin_required, login_required


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


def log_action(user_id, action):
    log = AuditLog(user_id=user_id, action=action)
    db.session.add(log)
    db.session.commit()

# Manage Users
@admin_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def get_all_users():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    query = User.query.paginate(page=page, per_page=limit, error_out=False)
    users = query.items
    log_action(session['user_id'], "Accessed Manage Users")

    return jsonify({
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "role": u.role,
                "is_suspended": u.is_suspended
            } for u in users
        ],
        "total": query.total,
        "page": query.page,
        "pages": query.pages
    })

@admin_bp.route('/users/<int:user_id>/suspend-toggle', methods=['POST'])
@login_required
@admin_required
def toggle_suspend(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.is_suspended = not user.is_suspended
    db.session.commit()
    action = "Suspended" if user.is_suspended else "Unsuspended"
    log_action(session['user_id'], f"{action} user {user.email}")
    return jsonify({"message": f"User {action.lower()} successfully"})

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    log_action(session['user_id'], f"Deleted user {user.email}")
    return jsonify({"message": "User deleted successfully"})
