import os
import token

class Config:
    BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")
    confirm_url = f"{BASE_URL}/confirm/{token}"
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///nextstep.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'sandbox.smtp.mailtrap.io'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'c6cd4bf2bd27a0'
    MAIL_PASSWORD = 'dc1b8cb5351ced'
    MAIL_DEFAULT_SENDER = 'noreply@nextstep.com'

