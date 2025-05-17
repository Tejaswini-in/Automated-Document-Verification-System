from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)

    # Import models here so they are registered before create_all()
    from models.user import User
    from models.document import Document
    from models.audit_log import AuditLog
    from models.data import Data
    


    with app.app_context():
        db.create_all()
