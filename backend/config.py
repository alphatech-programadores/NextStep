import os

class Config:
    BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
    # Si la carpeta 'instance' está en el mismo nivel que app.py y config.py está en la misma carpeta:
    # Si config.py está en la raíz de backend y 'instance' también:
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'nextstep.db')
    # Prueba con esta ruta que es muy común si 'instance' está en la raíz del proyecto Flask:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.getcwd(), 'instance', 'nextstep.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('GMAIL_USER')
    MAIL_PASSWORD = os.getenv('GMAIL_PASS')
    MAIL_DEFAULT_SENDER = os.getenv('GMAIL_USER')


    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')   
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # Límite de 16 MB para subidas (ejemplo)
    ALLOWED_EXTENSIONS_CV = {'pdf', 'doc', 'docx'} # Extensiones permitidas para CV
    ALLOWED_EXTENSIONS_IMG = {'png', 'jpg', 'jpeg', 'gif'} # Extensiones permitidas para imágenes