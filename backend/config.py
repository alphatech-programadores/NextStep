import os

# Obtiene la ruta base del proyecto de forma más segura
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # ✅ Usa una variable de entorno para la URL base en producción
    BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")
    
    # ✅ El secreto debe venir de una variable de entorno en producción
    SECRET_KEY = os.getenv("SECRET_KEY", "un-secreto-muy-dificil-de-adivinar")

    # --- CONFIGURACIÓN DE BASE DE DATOS (CORREGIDA) ---
    # Lee la variable de entorno de Render. Si no existe, usa SQLite para desarrollo local.
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'nextstep.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- CONFIGURACIÓN DE CORREO (SE MANTIENE IGUAL) ---
    # ✅ Bien hecho usando variables de entorno para las credenciales
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('GMAIL_USER')
    MAIL_PASSWORD = os.getenv('GMAIL_PASS')
    MAIL_DEFAULT_SENDER = os.getenv('GMAIL_USER')

    # --- CONFIGURACIÓN DE SUBIDA DE ARCHIVOS (CORREGIDA) ---
    # Para Render, debes usar un Render Disk. El disco se monta en una ruta como '/mnt/data'.
    # Debes crear esta carpeta 'uploads' dentro de tu disco.
    # En local, seguirá usando una carpeta 'uploads' en tu proyecto.
    UPLOAD_FOLDER = os.getenv('RENDER_DISK_PATH', os.path.join(basedir, 'uploads'))
    
    # ✅ La URL para ver los archivos subidos debe ser dinámica
    UPLOADED_FILES_BASE_URL = f"{BASE_URL}/static/uploads" # O la ruta que configures para servir los archivos

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS_CV = {'pdf', 'doc', 'docx'}
    ALLOWED_EXTENSIONS_IMG = {'png', 'jpg', 'jpeg', 'gif'}