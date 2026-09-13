import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "studyos_super_secret_key_2026"

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" + os.path.join(BASE_DIR, "instance", "studyos.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_PERMANENT = False

    REMEMBER_COOKIE_DURATION = 86400

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024