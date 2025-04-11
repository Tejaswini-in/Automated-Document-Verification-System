from dotenv import load_dotenv
import os

load_dotenv()

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret")
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///verification.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False
