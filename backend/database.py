from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)  # ✅ This is what you're missing

    # Import models here so they are registered before create_all()
    from models.user import User
    from models.document import Document
    


    with app.app_context():
        db.create_all()
