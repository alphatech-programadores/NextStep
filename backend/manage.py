from app import create_app
from extensions import db, migrate
from models import user, student_profile, institution_profile, application, vacant

app = create_app()

# Si quieres que Migrate esté disponible para CLI
migrate.init_app(app, db)
