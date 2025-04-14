import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.verification_routes import verify_bp
from routes.admin_routes import admin_bp
from database import db, init_db

app = Flask(__name__)
app.config.from_pyfile("config.py")
CORS(app)

# Initialize the database
init_db(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(verify_bp, url_prefix='/verify')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
