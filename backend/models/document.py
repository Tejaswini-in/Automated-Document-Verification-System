from database import db

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    doc_type = db.Column(db.String(50))
    file_path = db.Column(db.String(200))
    status = db.Column(db.String(50))  # Verified, Rejected, Pending
    result_data = db.Column(db.Text)
