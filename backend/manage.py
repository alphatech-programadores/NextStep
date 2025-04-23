from app import create_app
from extensions import db, migrate
from flask_migrate import upgrade

app = create_app()

# Aplica migraciones automáticamente al arrancar (solo mientras no tienes shell)
with app.app_context():
    upgrade()
