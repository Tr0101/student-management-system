import os
from dotenv import load_dotenv
from pathlib import Path

# 🔹 Load biến môi trường từ file .env
load_dotenv()

class Config:
    # ========= 🔐 Cấu hình bảo mật =========
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")

    # ========= 🗄️ Cấu hình Database =========
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        f"sqlite:///{Path('instance').absolute() / 'app.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ========= 📧 Cấu hình Email (Flask-Mail) =========
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() in ["true", "1", "t"]
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")  # ví dụ: your_email@gmail.com
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")  # App password (16 ký tự)
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)

    # ========= 🧩 CSRF =========
    WTF_CSRF_ENABLED = True
