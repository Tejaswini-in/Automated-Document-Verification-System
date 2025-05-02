import sys
from flask import Flask, send_from_directory
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from flask import Flask
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.verification_routes import verify_bp
from routes.admin_routes import admin_bp
from routes.user_upload import user_upload
from database import db, init_db

app = Flask(__name__)
app.config.from_pyfile("config.py")
# CORS(app)
# Enable CORS with credentials support
CORS(app, supports_credentials=True)

# Initialize the database
init_db(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(verify_bp, url_prefix='/verify')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(user_upload, url_prefix='/api/user')

# 🆕 Serve static uploads
@app.route('/uploads/<filename>')
def serve_uploaded_file(filename):
    upload_folder = os.path.abspath("uploads")  # Adjust if needed
    return send_from_directory(upload_folder, filename)
print(app.url_map)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
