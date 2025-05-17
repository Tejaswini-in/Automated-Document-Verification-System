from database import db

class Data(db.Model):
    __tablename__ = 'data'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    id_number = db.Column(db.String(20), nullable=False, unique=True)
    document_type = db.Column(db.String(50), nullable=False)
    keywords = db.Column(db.String(200), nullable=True, default='')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<Data {self.name} - {self.id_number}>' 